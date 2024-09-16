import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained("rtzr/ko-gemma-2-9b-it")
model = AutoModelForCausalLM.from_pretrained("rtzr/ko-gemma-2-9b-it", torch_dtype=torch.float16).to(device)

input_text = "오늘 날씨 어때?"

input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)

with torch.no_grad():
    output = model.generate(input_ids, max_length=100, do_sample=True, temperature=0.7)

generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)
