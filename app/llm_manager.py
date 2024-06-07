from transformers import pipeline, LlamaForCausalLM, AutoTokenizer
import torch

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

    #adds system prompt to messages, takes context as optional argument
    def add_system_prompt(self, system_prompt: str, context: str = None):
        if not context:
            self.messages.append({
                "role": "system", 
                "content": system_prompt
            })
        else:
            content = system_prompt + """
            Answer the questions based on the context below:
            """ + context
            self.messages.append({
                "role": "system", 
                "content": content
            })

    # appends a message of role user to messages
    def add_message_user(self, message_user: str):
        self.messages.append({"role": "user",
                              "content": message_user})
    
    # appends a message of role assistant to messages
    def add_message_llm(self, message_llm: str):
        self.messages.append({"role": "assistant",
                              "content": message_llm})
    
    #generates a new assistant message based on the messages list
    def generate_response(self, user_prompt: str):
        self.add_message_user(user_prompt)

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

        # generates a new message from the tokenized prompt
        outputs = self.pipeline(
            prompt,
            max_new_tokens=512,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )

        # update message list with new response and returns
        self.add_message_llm(outputs[0]["generated_text"][len(prompt):])
        return outputs[0]["generated_text"][len(prompt):]

    