from llm_manager import LLM_Manager
from langchain_community.document_loaders import PyPDFLoader
from transformers import LlamaForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

loader = PyPDFLoader("./sample_filled_in_MR.pdf")

system_prompt = "You are a helpful assistant. If you don't know the answer say you don't know."

bits_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
model = LlamaForCausalLM.from_pretrained("../../Meta-Llama-3-8B-Instruct", quantization_config=bits_config)
tokenizer = AutoTokenizer.from_pretrained("../../Meta-Llama-3-8B-Instruct")
chat = LLM_Manager(model=model, tokenizer=tokenizer, system_prompt=system_prompt)

question = "Can the patient read the time from a watch?"
print(chat.generate_response(user_prompt=question, loader=loader))