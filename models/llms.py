# *************** IMPORT FRAMEWORK *************** 
from langchain.chat_models import ChatOpenAI
from setup import OPENAI_API_KEY

class LLMModels:
    """
    Define LLM models with OpenAI
    """
    def __init__(self):
        self.llm_cv = self.create_llm_cv()

    def create_llm_cv(self):
        llm_chat = ChatOpenAI(
            temperature=0.1, 
            openai_api_key=OPENAI_API_KEY, 
            model_name="gpt-3.5-turbo-0125"
        )

        return llm_chat