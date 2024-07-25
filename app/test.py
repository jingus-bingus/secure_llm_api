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

url = "https://127.0.0.1:5000/conversation"

session = requests.Session()
data = {'prompt': 'Give a summary of the patient\'s information.', 'user_id' : 3, 'file': 'sample_filled_in_MR.pdf'}
response = session.post(url, json=data, verify=False).json()
print(response)

# data = {'prompt': 'Who discovered this?', 'user_id': 3, 'conversation_id' : response['conversation_id']}
# response = session.put(url, json=data, verify=False).json()
# print(response['output'])

# print(response)