# backend/rag_handler.py

import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


# 벡터 데이터베이스를 저장할 디렉토리
CHROMA_DB_DIRECTORY = "chroma_db"

def get_embeddings_model():
    """Google Generative AI 임베딩 모델을 초기화하고 반환합니다."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    
    # 텍스트 임베딩에 권장되는 모델 사용
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=api_key)

def process_and_store_document(material_id: int, document_text: str):
    """
    문서를 처리하여 조각으로 나누고, 임베딩을 생성한 뒤,
    해당 자료 전용 ChromaDB 컬렉션에 저장합니다.
    """
    if not document_text or not document_text.strip():
        print(f"[RAG] Material ID {material_id}: 문서 내용이 비어있어 처리를 건너뜁니다.")
        return

    # 1. 문서를 의미있는 조각(chunk)으로 분할
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
        # 2. 임베딩 모델 가져오기
        embeddings = get_embeddings_model()

        # 3. 이 자료만을 위한 고유한 컬렉션 생성 및 저장
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
    collection_name = f"material_{material_id}"
    
    vector_store = Chroma(
        collection_name=collection_name,
        persist_directory=CHROMA_DB_DIRECTORY,
        embedding_function=embeddings
    )
    # k=4는 가장 관련성 높은 4개의 조각을 검색하라는 의미입니다.
    return vector_store.as_retriever(search_kwargs={"k": 4})

def generate_rag_response(material_id: int, question: str):
    """
    RAG 파이프라인을 실행하여 사용자의 질문에 대한 답변을 생성합니다.
    1. Retriever로 관련 문서 검색
    2. 프롬프트 생성
    3. LLM으로 답변 생성
    """
    try:
        retriever = get_retriever_for_material(material_id)
        
        # 프롬프트 템플릿 정의
        template = """
        당신은 주어진 내용을 바탕으로 질문에 답변하는 AI 어시스턴트입니다.
        내용을 벗어난 질문이나, 내용에서 답을 찾을 수 없는 경우에는 "제공된 문서의 내용만으로는 답변할 수 없습니다."라고 답변해주세요.
        답변은 항상 한국어로 해주세요.

        내용:
        {context}

        질문:
        {question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        # LLM 모델 초기화
        api_key = os.getenv("GEMINI_API_KEY")
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0)

        # LangChain Expression Language (LCEL)을 사용한 RAG 체인 구성
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )

        # 체인 실행 및 답변 반환
        answer = rag_chain.invoke(question)
        return answer
    except Exception as e:
        print(f"[RAG] Material ID {material_id}: 답변 생성 중 오류 발생: {e}")
        # 실제 프로덕션에서는 더 상세한 오류 처리가 필요합니다.
        return "답변을 생성하는 중 오류가 발생했습니다. 데이터가 올바르게 처리되었는지 확인해주세요."