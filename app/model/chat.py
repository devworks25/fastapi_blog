import os
from functools import lru_cache
from urllib.parse import quote

from langchain.agents import create_agent
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda, RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from .rag_retrieval import format_documents, retrieve_documents, search_faq


SESSION_TTL_SECONDS = 30 * 60


def redis_url() -> str:
    configured_url = os.getenv("REDIS_URL")
    if configured_url:
        return configured_url

    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    password = os.getenv("REDIS_PASSWORD", "")
    if password:
        return f"redis://:{quote(password, safe='')}@{host}:{port}/0"
    return f"redis://{host}:{port}/0"


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url=redis_url(),
        ttl=SESSION_TTL_SECONDS,
    )


def clear_session(session_id: str) -> None:
    get_session_history(session_id).clear()


@lru_cache(maxsize=1)
def get_chat_chain() -> RunnableWithMessageHistory:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not configured")
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY is not configured")

    llm = ChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"), temperature=0)
    tools = [search_faq, TavilySearch(max_results=5, topic="general")]
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a helpful FAQ assistant. Treat supplied PDF excerpts as the source of truth "
            "for company-specific questions. Use FAQ search for additional policy details and web "
            "search for current or externally verifiable facts. Never use web results to invent "
            "company policies. If the available sources do not answer the question, say so."
        ),
    )

    def run_agent(state: dict) -> dict:
        user_message = HumanMessage(
            content=f"{state['input']}\n\nRelevant PDF excerpts:\n{state['context']}"
        )
        result = agent.invoke({"messages": [*state.get("chat_history", []), user_message]})
        final_message = next(
            (
                message
                for message in reversed(result["messages"])
                if isinstance(message, AIMessage) and not message.tool_calls
            ),
            None,
        )
        if final_message is None:
            raise RuntimeError("The chat agent did not return a final answer.")

        answer = final_message.content
        if not isinstance(answer, str):
            answer = "".join(
                block.get("text", "") for block in answer if isinstance(block, dict)
            )
        return {"output": answer}

    return RunnableWithMessageHistory(
        RunnableLambda(run_agent),
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="output",
    )


def answer_question(question: str, session_id: str) -> dict:
    documents = retrieve_documents(question)
    result = get_chat_chain().invoke(
        {"input": question, "context": format_documents(documents)},
        config={"configurable": {"session_id": session_id}},
    )
    return {"answer": result["output"], "context": documents}