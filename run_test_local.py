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
    video_id = "jb2f-yxcbRA"  # 비디오 ID 설정
    collect_time = 20  # 크롤링 시간 (초)

    # Chat_Crawler 인스턴스 생성 및 크롤링 수행
    crawler = Chat_Crawler(collect_time=collect_time, youtube_api_key=api_key, video_id=video_id)
    crawler.do_crawling()

    # Step 2: 크롤링한 댓글 요약
    print("=== Step 2: 댓글 요약 시작 ===")
    model_name = "rtzr/ko-gemma-2-9b-it"  # 모델 이름
    chat_file_path = f'./data/{video_id}_chat.csv'  # 크롤링한 데이터 파일 경로

    # CommentSummarizer 인스턴스 생성 및 요약 수행
    summarizer = CommentSummarizer(model_name=model_name)
    summarizer.set_chat_file_path(chat_file_path)
    # 입력 프롬프트
    prompt_template = """{comments}

위의 유튜브 라이브 채팅 댓글을 읽고, 주제와 대화의 흐름을 파악하여 아래의 형식으로 **부드럽고 친근한 어조로 존댓말로** 요약해줘:

1. 첫 번째 요약 내용
2. 두 번째 요약 내용
3. 세 번째 요약 내용

요약 예시: 
1. 시청자들은 스트리밍 중 게스트 등장에 신기해 합니다.
2. 시청자들은 스트리머의 시간을 끌고 고민하는 모습이 지루합니다.
3. 시청자들은 게스트들의 대화 내용이 너무 재미있습니다.

긍정:XX/부정:XX

- 위의 형식에 맞춰 요약 내용을 작성해 주고, 흐름을 이해할 수 있을 정도의 구체적인 키워드를 포함해줘.
- **요약 시 부드럽고 자연스러운 표현을 사용해줘.**
- 긍정과 부정의 비율은 전체 100%를 기준으로 계산해줘.
- 다른 불필요한 말은 생략하고, 위의 형식으로만 출력해줘.
"""

    # 요약 결과 생성
    summary = summarizer.summarize(prompt_template)
    
    # 요약 결과 출력
    print("=== 요약 결과 ===")
    print(summary)

if __name__ == "__main__":
    main()
