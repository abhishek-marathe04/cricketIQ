import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_openai import ChatOpenAI
from openai import OpenAI, RateLimitError
from langchain_community.llms import HuggingFaceHub
from together import Together
from config import TOGETHER_API_KEY, GROQ_API_KEY
from utils.logger import get_logger
from stats.common_functions.custom_exceptions import AllModelsRateLimitedError

logger = get_logger()

# Models listed in order of preference (best reasoning first)
GROQ_FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
]

def get_llm_client(env="local"):
    if env == "prod":
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY,
        )
    else:
        return OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",  # Dummy
        )

def get_model_name(env="local"):
    if env == "prod":
        return GROQ_FALLBACK_MODELS[0]
    else:
        return "model-identifier"

def call_llm_with_fallback(env="local", messages=None, **kwargs):
    """
    Calls Groq LLM with automatic model fallback on rate limit (429).
    Tries models in GROQ_FALLBACK_MODELS order. In local env, uses get_llm_client directly.
    """
    if messages is None:
        messages = []

    if env != "prod":
        client = get_llm_client(env=env)
        model = get_model_name(env=env)
        return client.chat.completions.create(model=model, messages=messages, **kwargs)

    client = get_llm_client(env="prod")

    for model in GROQ_FALLBACK_MODELS:
        try:
            logger.info(f"Trying model: {model}")
            response = client.chat.completions.create(model=model, messages=messages, **kwargs)
            logger.info(f"Success with model: {model}")
            return response
        except RateLimitError as e:
            logger.warning(f"Rate limit hit for {model}, trying next model. Error: {e}")

    raise AllModelsRateLimitedError()