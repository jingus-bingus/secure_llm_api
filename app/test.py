# from llm_manager import LLM_manager
# from transformers import LlamaForCausalLM, AutoTokenizer, BitsAndBytesConfig
# import torch

# model_dir = '../../Meta-Llama-3-8B-Instruct'

# bits_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)

# model = LlamaForCausalLM.from_pretrained(model_dir, quantization_config=bits_config)
# tokenizer = AutoTokenizer.from_pretrained(model_dir)


# chat = LLM_manager(model=model, tokenizer=tokenizer)
# chat.add_system_prompt("You are a helpful assistant. Answer the questions succinctly.")
# response = chat.generate_response("Is chocolate healthy for you?")
# print(response)

import requests

url = "http://127.0.0.1:5000/conversation"

session = requests.Session()
data = {'prompt': 'Why is the sky blue?'}
response = session.post(url, json=data).json()
print(response['output'])

data = {'prompt': 'Who discovered this?'}
response = session.put(url, json=data).json()
print(response['output'])

print(response)