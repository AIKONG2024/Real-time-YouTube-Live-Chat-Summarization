import os
from dotenv import load_dotenv

# Chat_Crawler 및 CommentSummarizer 클래스 임포트
from chat_crawler import Chat_Crawler  # 채팅 크롤링 클래스
from summarizer import CommentSummarizer  # 댓글 요약 클래스

def main():
    # .env 파일에서 API 키 로드
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')

    # Step 1: 채팅 크롤링
    print("=== Step 1: 채팅 크롤링 시작 ===")
    video_id = "w3YN5dH1JaQ"  # 비디오 ID 설정
    channel_name = "mudo"  # 채널명 설정
    collect_time = 10  # 크롤링 시간 (초)

    # Chat_Crawler 인스턴스 생성 및 크롤링 수행
    crawler = Chat_Crawler(collect_time=collect_time, youtube_api_key=api_key, video_id=video_id, channel_name=channel_name)
    crawler.do_croling()

    # Step 2: 크롤링한 댓글 요약
    print("=== Step 2: 댓글 요약 시작 ===")
    model_name = "rtzr/ko-gemma-2-9b-it"  # 모델 이름
    chat_file_path = f'./data/news_{channel_name}_yt.csv'  # 크롤링한 데이터 파일 경로

    # CommentSummarizer 인스턴스 생성 및 요약 수행
    summarizer = CommentSummarizer(model_name=model_name, chat_file_path=chat_file_path)
    
    # 입력 프롬프트
    prompt_template = "{comments} 이건 유튜브 라이브채팅 댓글이야. 어떤 주제를 가지고 얘기를 하고 있고, 대화의 흐름을 파악해서 주제를 3줄로 요약해줘."

    # 요약 결과 생성
    summary = summarizer.summarize(prompt_template)
    
    # 요약 결과 출력
    print("=== 요약 결과 ===")
    print(summary)

if __name__ == "__main__":
    main()
