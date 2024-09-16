import torch
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline
import bitsandbytes as bnb  # For quantization

# GPU 설정 (0번 GPU를 사용하고, float16으로 설정)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# 토크나이저 및 모델 로드 (8-bit 양자화 모델 로드)
tokenizer = AutoTokenizer.from_pretrained("rtzr/ko-gemma-2-9b-it")
model = AutoModelForCausalLM.from_pretrained(
    "rtzr/ko-gemma-2-9b-it", 
    load_in_8bit=True,  # 8-bit quantization
    device_map='auto',  # Automatically selects the device (GPU)
)

# 파일 경로 설정 및 데이터 읽기
file_path = './data/news_ytn_yt.csv'
data = pd.read_csv(file_path)

# 댓글 내용 가져오기
comments = data['댓글 내용'].tolist()

# 사용자 입력에 따른 메시지
messages = [
    {"role": "summarization", "content": f"{comments} 이건 유튜브 라이브채팅 댓글이야. 어떤 주제를 가지고 얘기를 하고 있고, 대화의 흐름을 파악해서 주제를 3줄로 요약해줘."}
]

# 텍스트 생성
for message in messages:
    prompt = message["content"]
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)  # Only the input needs to be moved to the device
    
    with torch.no_grad():
        output = model.generate(input_ids, max_length=5000, do_sample=True, temperature=0.7)
    
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(generated_text)