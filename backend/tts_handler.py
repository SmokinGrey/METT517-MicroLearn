
import os
import uuid
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

def create_audio_briefing(text: str) -> str | None:
    """
    요약 텍스트를 받아 OpenAI TTS를 사용하여 오디오 파일을 생성하고,
    해당 파일에 접근할 수 있는 URL을 반환합니다.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("경고: OPENAI_API_KEY가 설정되지 않았습니다. 오디오 브리핑을 생성할 수 없습니다.")
        return None

    try:
        client = OpenAI(api_key=api_key)

        # 오디오 파일을 저장할 경로 설정
        # Path(__file__).parent는 현재 파일(tts_handler.py)이 있는 디렉토리를 가리킵니다.
        speech_folder_path = Path(__file__).parent / "static" / "audio"
        speech_folder_path.mkdir(parents=True, exist_ok=True)
        
        # 고유한 파일명 생성
        file_name = f"{uuid.uuid4()}.mp3"
        speech_file_path = speech_folder_path / file_name

        print(f"오디오 파일 생성 중: {speech_file_path}")

        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )

        # 스트리밍 방식으로 파일 저장
        response.stream_to_file(speech_file_path)

        print(f"오디오 파일 저장 완료: {speech_file_path}")

        # 프론트엔드에서 접근할 수 있는 URL 경로 반환
        return f"/static/audio/{file_name}"

    except Exception as e:
        print(f"오디오 브리핑 생성 중 오류 발생: {e}")
        return None

