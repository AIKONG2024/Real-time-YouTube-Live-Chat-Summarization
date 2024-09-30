import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class CommentSummarizer:
    def __init__(self, model_name):
        # 모델과 토크나이저 초기화
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            load_in_8bit=True,  # 8-bit quantization
            device_map='auto',  # Automatically selects the device (GPU)
        )
        self.chat_file_path = None

    def set_chat_file_path(self, chat_file_path):
        self.chat_file_path = chat_file_path

    def load_chat(self):
        # 채팅 데이터를 로드하고 전처리
        if self.chat_file_path:
            with open(self.chat_file_path, 'r', encoding='utf-8') as f:
                comments = f.read()
            return comments
        else:
            return ""

    def summarize(self, prompt_template, should_stop=None, max_length=500, temperature=0.7):
        comments = self.load_chat()
        prompt = prompt_template.format(comments=comments)
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
        prompt_length = input_ids.shape[-1]

        # 텍스트 생성 설정
        generate_kwargs = {
            'input_ids': input_ids,
            'max_length': prompt_length + max_length,
            'do_sample': True,
            'temperature': temperature,
            'pad_token_id': self.tokenizer.eos_token_id,
        }

        # 생성 진행 중에 중단 여부 확인
        output = input_ids
        try:
            with torch.no_grad():
                for _ in range(0, max_length, 50):  # 50 토큰씩 생성
                    if should_stop and should_stop():
                        print("요약 작업 중단됨")
                        return "요약 작업이 중단되었습니다."
                    output = self.model.generate(
                        input_ids=output,
                        max_length=output.shape[1] + 50,
                        do_sample=True,
                        temperature=temperature,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )
        except Exception as e:
            print(f"요약 중 에러 발생: {str(e)}")
            return f"요약 중 에러 발생: {str(e)}"

        generated_tokens = output[0, prompt_length:]
        generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        return generated_text.strip()
