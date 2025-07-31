from langchain_chroma import Chroma
from langchain_community.vectorstores import  FAISS
from langchain_huggingface import HuggingFaceEmbeddings



class EVR:
    def __init__(self,model_name="all-MiniLM-L6-v2",persist_directory="./vector_db_BSA",k=10,dbtype="chroma"):
        self.embedding = HuggingFaceEmbeddings(model_name=model_name)
        self.vectordb_chroma = Chroma(persist_directory=persist_directory, embedding_function=self.embedding)
        self.retriever = self.vectordb_chroma.as_retriever(search_kwargs={"k": k})
        self.db_type=dbtype
        
    def get_embedding(self):
        return self.embedding
    
    def get_vectordb(self):
        if self.db_type=="chroma":
            return self.vectordb_chroma
    
    def get_retriever(self):
        return self.retriever
