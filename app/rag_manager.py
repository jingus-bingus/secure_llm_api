from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

class RAG_manager:
    def __init__(self, loader: PyPDFLoader = None):
        if loader:
            self.loader = loader

    def remove_chars_at_indices(self, s, indices):
        # Convert the string to a list of characters
        chars = list(s)
        
        # Sort indices in reverse order to avoid index shifting issues
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(chars):
                del chars[index]
        
        # Convert the list back to a string
        return ''.join(chars)

    # retrieves context relevant to question from documents passed in loader
    def retrieve_context(self, question: str, loader: PyPDFLoader = None):
        if loader:
            self.loader = loader

        documents = self.loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)

        # creates a vector store of the documents passed in loader
        embedding_function = SentenceTransformerEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        vectorstore = Chroma(collection_name="sample_collection", embedding_function = embedding_function)
        vectorstore.add_documents(texts)

        # performs a similarity search on the question to pick relative context
        retriever = vectorstore.as_retriever(k=3)
        self.docs = retriever.invoke(question)
        content = "\n\n".join([d.page_content for d in self.docs])

        indeces = []
        for index, char in enumerate(content):
            if char == "\uF0A8":
                for i in range (0,5):
                    indeces.append(index+i)
            elif char == "\uF0FE":
                indeces.append(index)

        
        self.content = self.remove_chars_at_indices(content, indeces)

        # print(self.content)

        return self.content