from repository.vector_db import VectorDB
from service.llm_service import get_chat_response


class ConversationService:

    def chat(self, query: str, user_id: int, vdb: VectorDB):
        prompt = vdb.get_prompt(query, user_id)
        context = vdb.get_context(prompt, user_id)
        llm_response = get_chat_response(prompt, context=context)
        return llm_response
