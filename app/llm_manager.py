from transformers import pipeline, LlamaForCausalLM, AutoTokenizer
from langchain_community.document_loaders import PyPDFLoader
import torch
import time
from rag_manager import RAG_manager

class LLM_Manager:
    def __init__(self, model: LlamaForCausalLM.from_pretrained, 
                 tokenizer: AutoTokenizer.from_pretrained, 
                 messages: list = None, 
                 context: str = None, 
                 system_prompt: str = None):
        # initialize transformers pipeline for inference
        self.pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            model_kwargs={"torch_dtype": torch.bfloat16},
        )
        # load list of messages or create empty list
        if messages:
            self.messages = messages
        else:
            self.messages = []
        
        # adds system prompt if provided
        if system_prompt:
            self.add_system_prompt(system_prompt, context)

        self.time_generation = None

    #adds system prompt to messages, takes context as optional argument
    def add_system_prompt(self, system_prompt: str, context: str = None):
        if not context:
            self.messages.append({
                "role": "system", 
                "content": system_prompt
            })
        elif context:
            content = system_prompt + """
            Answer the questions based on the context below:
            """ + context

            self.messages.append({
                "role": "system", 
                "content": content
            })

    # appends a message of role user to messages
    def add_message_user(self, message_user: str, loader: PyPDFLoader = None):
        if not loader:
            self.messages.append({"role": "user",
                                "content": message_user})
        else:
            rag = RAG_manager(loader=loader)
            content = """
            Answer the questions based on the context below:
            """ + rag.retrieve_context(question=message_user) + """
            Question: 
            """ + message_user

            self.messages.append({"role": "user",
                                "content": content})
    
    # appends a message of role assistant to messages
    def add_message_llm(self, message_llm: str):
        self.messages.append({"role": "assistant",
                              "content": message_llm})
    
    #generates a new assistant message based on the messages list
    def generate_response(self, user_prompt: str, loader: PyPDFLoader = None):
        self.add_message_user(user_prompt, loader)

        # tokenizes messages list as prompt
        prompt = self.pipeline.tokenizer.apply_chat_template(
            self.messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        start = time.time()
        # generates a new message from the tokenized prompt
        outputs = self.pipeline(
            prompt,
            max_new_tokens=512,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        end = time.time()
        self.time_generation = (end - start) * 10**3

        # update message list with new response and returns
        self.add_message_llm(outputs[0]["generated_text"][len(prompt):])
        return outputs[0]["generated_text"][len(prompt):]