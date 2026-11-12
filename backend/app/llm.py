import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.app.config import MUSE_MODEL, MUSE_BASE_URL, MUSE_API_KEY, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger(__name__)

def get_llm(temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> ChatOpenAI:
    temp = temperature if temperature is not None else TEMPERATURE
    tokens = max_tokens if max_tokens is not None else MAX_TOKENS
    return ChatOpenAI(
        model=MUSE_MODEL,
        api_key=MUSE_API_KEY,
        base_url=MUSE_BASE_URL,
        max_tokens=tokens,
        temperature=temp,
        timeout=120.0
    )

async def call_agent_llm_async(system_prompt: str, user_prompt: str, temperature: Optional[float] = None) -> str:
    llm = get_llm(temperature=temperature)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    try:
        response = await llm.ainvoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"Error calling LLM async: {e}")
        raise e

def call_agent_llm_sync(system_prompt: str, user_prompt: str, temperature: Optional[float] = None) -> str:
    llm = get_llm(temperature=temperature)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"Error calling LLM sync: {e}")
        raise e
