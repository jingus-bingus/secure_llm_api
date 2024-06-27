from transformers import pipeline, LlamaForCausalLM, AutoTokenizer
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
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
        elif context:
            content = system_prompt + """
            Answer the questions based on the context below:
            """ + context
            self.messages.append({
                "role": "system", 
                "content": content
            })

    def retrieve_context(self, loader: PyPDFLoader, question: str):
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        embedding_function = SentenceTransformerEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        vectorstore = Chroma(collection_name="sample_collection", embedding_function = embedding_function)
        vectorstore.add_documents(texts)
        retriever = vectorstore.as_retriever(k=7)

        docs = retriever.invoke(question)

        return "\n\n".join([d.page_content for d in docs])

    # appends a message of role user to messages
    def add_message_user(self, message_user: str, loader: PyPDFLoader = None):
        if not loader:
            self.messages.append({"role": "user",
                                "content": message_user})
        else:
            content = """
            Answer the questions based on the context below:
            """ + self.retrieve_context(loader, question=message_user) + """
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

    