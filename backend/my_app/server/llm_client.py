"""
Shared LangChain-based LLM client factory.

Kept separate from chat_handler (which is now LangChain-free) so that
security_tools and voice_agent can still use LangChain's streaming/ainvoke
interface until they're migrated individually.
"""

import os


def get_llm_client(api: str, model: str):
    """Return a LangChain chat model for the given provider."""
    if api == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, api_key=os.getenv("OPENAI_API_KEY"))
    if api == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, api_key=os.getenv("GROQ_API_KEY"))
    raise ValueError(f"Unsupported API: {api}")
