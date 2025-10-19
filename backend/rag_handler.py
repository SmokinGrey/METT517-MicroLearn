# backend/rag_handler.py

import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# 벡터 데이터베이스를 저장할 디렉토리
CHROMA_DB_DIRECTORY = "chroma_db"

def get_embeddings_model():
    """
    Google Generative AI 임베딩 모델을 초기화하고 반환합니다.
    API 키가 없으면 None을 반환하여 RAG 기능을 비활성화합니다.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("[RAG 경고] GEMINI_API_KEY가 설정되지 않았습니다. '자료와 대화하기' 기능이 비활성화됩니다.")
        return None
    
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=api_key)

def process_and_store_document(material_id: int, document_text: str):
    """
    문서를 처리하여 조각으로 나누고, 임베딩을 생성한 뒤,
    해당 자료 전용 ChromaDB 컬렉션에 저장합니다.
    """
    embeddings = get_embeddings_model()
    if embeddings is None:
        return

    if not document_text or not document_text.strip():
        print(f"[RAG] Material ID {material_id}: 문서 내용이 비어있어 처리를 건너뜁니다.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_text(document_text)
    
    if not chunks:
        print(f"[RAG] Material ID {material_id}: 문서에서 텍스트 조각을 생성할 수 없습니다.")
        return

    try:
        collection_name = f"material_{material_id}"
        
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=CHROMA_DB_DIRECTORY
        )
        
        print(f"[RAG] Material ID {material_id}: 문서 처리 및 벡터 저장을 완료했습니다. ({len(chunks)}개 조각)")
        return vector_store

    except Exception as e:
        print(f"[RAG] Material ID {material_id}: 문서 처리 중 오류 발생: {e}")
        return None

def get_retriever_for_material(material_id: int):
    """지정된 material_id에 대한 retriever를 로드하고 반환합니다."""
    embeddings = get_embeddings_model()
    if embeddings is None:
        return None

    collection_name = f"material_{material_id}"
    
    vector_store = Chroma(
        collection_name=collection_name,
        persist_directory=CHROMA_DB_DIRECTORY,
        embedding_function=embeddings
    )
    return vector_store.as_retriever(search_kwargs={"k": 3}) # 근거 자료 3개 조회

async def stream_rag_response(material_id: int, question: str):
    """
    RAG 파이프라인을 실행하여 답변과 근거 문서를 스트리밍으로 생성합니다.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        yield json.dumps({"type": "error", "data": "현재 API 키가 설정되지 않아 '자료와 대화하기' 기능을 사용할 수 없습니다."})
        return

    try:
        retriever = get_retriever_for_material(material_id)
        if retriever is None:
            raise ValueError("Retriever를 초기화할 수 없습니다. API 키 설정을 확인하세요.")
        
        # 1. 먼저 관련 문서를 검색합니다.
        relevant_docs = retriever.get_relevant_documents(question)
        
        # 2. 검색된 문서를 바탕으로 컨텍스트를 구성합니다.
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])

        template = """        당신은 주어진 내용을 바탕으로 질문에 답변하는 AI 어시스턴트입니다.
        내용을 벗어난 질문이나, 내용에서 답을 찾을 수 없는 경우에는 "제공된 문서의 내용만으로는 답변할 수 없습니다."라고 답변해주세요.
        답변은 항상 한국어로 해주세요.

        내용:
        {context}

        질문:
        {question}        """
        prompt = ChatPromptTemplate.from_template(template)
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0)
        
        chain = prompt | model | StrOutputParser()

        # 3. 답변을 스트리밍으로 생성하여 전송합니다.
        async for chunk in chain.astream({"context": context, "question": question}):
            yield json.dumps({"type": "token", "data": chunk})

        # 4. 답변 스트림이 끝난 후, 근거 문서(source)를 전송합니다.
        for doc in relevant_docs:
            yield json.dumps({"type": "source", "data": {"page_content": doc.page_content, "metadata": doc.metadata}})

    except Exception as e:
        print(f"[RAG] Material ID {material_id}: 스트리밍 중 오류 발생: {e}")
        yield json.dumps({"type": "error", "data": "스트리밍 답변 중 오류가 발생했습니다."})
