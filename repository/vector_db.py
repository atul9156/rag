import os
from collections import defaultdict
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader


class InMemoryStore:
    def __init__(self, search_relevance: int = os.getenv("SEARCH_RELEVANCE", 4)):
        # Only supports reading PDFs for the time being, need to make this more generic
        self.loader = PyPDFLoader
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=256,
            length_function=len,
            is_separator_regex=False,
        )
        self.embeddings_model = OpenAIEmbeddings(api_key=os.getenv("openai_api_key"))
        self.search_relevance = search_relevance
        self.db = defaultdict(list)
    
    def delete(self, user_id: int):
        if self.db[user_id] != []:
            del self.db[user_id]

    def generate_text_chunks(self, file_path: os.PathLike):
        """
        Reads text chunks from an uploaded file (pdf only) and returns a list of chunks.

        Args:
            file_path: os.PathLike object, Path of the file

        Returns:
            list: A list of text chunks (strings).
        """
        raw_document = self.loader(file_path).load()
        chunks = self.text_splitter.split_documents(raw_document)
        return chunks

    def encode_and_store(self, chunks, user_id):
        """Encodes data points and stores their vectors in memory."""
        self.db[user_id].append(FAISS.from_documents(chunks, self.embeddings_model))

    def get_context(self, query: str, user_id: int):
        """Searches for matching vectors based on a query vector."""
        matched_docs = []
        for db in self.db[user_id]:
            matched_docs.extend(db.similarity_search_with_score(query))
        matched_docs.sort(key=lambda x: x[1], reverse=True)

        return "\n\n".join([doc[0].page_content for doc in matched_docs[: self.search_relevance]])

    def get_prompt(self, query: str, user_id: int):
        # TODO: Implement a method to get a prompt for processing query correctly
        return query

    def get_refined_query(self, query):
        # TODO: Implement a method to refine the query for better search results (such as removing stopwords, adding synonyms, etc.)
        return query

    async def save_chunks_to_db(self, chunks):
        # This function is not used, remove it
        pass


DATA_STORES = {
    "in-memory": InMemoryStore,
    # other data stores can be defined here
}


class VectorDB:
    def __init__(self, data_store_type: str):
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("openai_api_key"))
        self.db = DATA_STORES.get(data_store_type.lower())
        if not self.db:
            raise NotImplementedError(
                f"Data store of type {data_store_type.lower()} is not yet implemented. Please choose one of {list(DATA_STORES.keys())}"
            )
        else:
            # Initialise Data Store object
            self.db = self.db()

    def delete(self, user_id: int):
        self.db.delete(user_id=user_id)

    def generate_text_chunks(self, file: os.PathLike):
        return self.db.generate_text_chunks(file)

    def encode_and_store(self, chunks, user_id: int):
        self.db.encode_and_store(chunks, user_id)

    def get_context(self, query: str, user_id: int):
        return self.db.get_context(query, user_id)

    def get_prompt(self, query: str, user_id: int):
        return self.db.get_prompt(query, user_id)

    # This funciton is not used
    async def get_refined_query(self, query):
        return await self.db.get_refined_query(query)

    # This function is not used
    async def save_chunks_to_db(self, chunks):
        await self.db.save_chunks_to_db(chunks)


vdb = VectorDB(data_store_type=os.getenv("data_store_type".upper(), "in-memory"))
