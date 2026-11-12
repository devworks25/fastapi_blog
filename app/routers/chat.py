import asyncio
import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, Response, status

from ..model.chat import SESSION_TTL_SECONDS, answer_question, clear_session
from ..model.rag_ingestion import NoRagDataError
from ..schemas.chat_schema import ChatRequest, ChatResponse


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
SESSION_COOKIE_NAME = "chat_session_id"
END_SESSION_MESSAGES = {"session:end", "ok", "end", "end session", "end chat", "goodbye", "bye"}


def format_chat_answer(answer: str) -> str:
    return (
        answer.replace(r"\\r\\n", "\n")
        .replace(r"\\n", "\n")
        .replace(r"\\t", "\t")
        .replace(r"\r\n", "\n")
        .replace(r"\n", "\n")
        .replace(r"\t", "\t")
    )


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    http_request: Request,
    response: Response,
) -> ChatResponse:
    session_id = (
        request.session_id
        or http_request.cookies.get(SESSION_COOKIE_NAME)
        or str(uuid4())
    )

    if request.session == "end" or request.question.strip().casefold() in END_SESSION_MESSAGES:
        try:
            await asyncio.to_thread(clear_session, session_id)
        except Exception as exc:
            logger.exception("Could not clear chat session")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not end the chat session.",
            ) from exc

        response.delete_cookie(SESSION_COOKIE_NAME, path="/chat", httponly=True, samesite="lax")
        return ChatResponse(
            session_id=session_id,
            question=request.question,
            answer="Your chat session has ended.",
            session_ended=True,
        )

    try:
        result = await asyncio.to_thread(answer_question, request.question, session_id)
    except NoRagDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat is unavailable. Check the OpenAI and Tavily API keys and Redis connection.",
        ) from exc

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        samesite="lax",
        path="/chat",
    )
    return ChatResponse(
        session_id=session_id,
        question=request.question,
        answer=format_chat_answer(result["answer"]),
    )