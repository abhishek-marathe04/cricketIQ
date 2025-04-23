import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_community.llms import HuggingFaceHub
from together import Together
from config import TOGETHER_API_KEY

def get_llm_client(env="local"):
    if env == "prod":
        return Together(api_key=TOGETHER_API_KEY)
    else:
        return OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",  # Dummy
        )
    
def get_model_name(env="local"):
    if env == "prod":
        return "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    else:
        return "model-identifier"