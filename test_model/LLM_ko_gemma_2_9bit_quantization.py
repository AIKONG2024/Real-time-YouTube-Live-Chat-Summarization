import torch
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 모델과 토크나이저 로드
model_name = "rtzr/ko-gemma-2-9b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, 
    load_in_4bit=True,  # 8-bit quantization
    device_map='auto',  
)

file_path = './data/jb2f-yxcbRA_chat.csv'
data = pd.read_csv(file_path)
comments = data['댓글 내용'].tolist()

# 사용자 입력에 따른 메시지
prompt = f"""{comments}

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

# 입력 텍스트를 토크나이즈 (여기서는 GPU로 이동할 필요가 없음)
inputs = tokenizer(prompt, return_tensors="pt")

# 모델이 실행되는 GPU로 텐서 전송
inputs = inputs.to(device)

# 텍스트 생성
with torch.no_grad():
    output = model.generate(inputs.input_ids, max_length=5000, do_sample=True, temperature=0.7)

# 생성된 텍스트를 디코딩
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)
