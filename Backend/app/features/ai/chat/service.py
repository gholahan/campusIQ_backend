import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from langchain_core.messages import HumanMessage as LangHumanMessage
from sqlmodel import select
from app.db.session import SessionDep

from app.common.enums import AiChatRole
from app.features.ai.chat.models import AICredit, AIConversation, AIMessage
from app.features.ai.chat.schemas import AIMessageRead, AIMessageResponse, PaginatedAIMessages
from app.features.documents.models import Document

logger = logging.getLogger(__name__)


async def _get_or_create_conversation(session: SessionDep, user_id: uuid.UUID) -> AIConversation:
    result = await session.exec(select(AIConversation).where(AIConversation.user_id == user_id))
    conversation = result.first()
    if not conversation:
        conversation = AIConversation(user_id=user_id)
        session.add(conversation)
        await session.flush()
    return conversation


async def get_user_conversation_id_service(session: SessionDep, user_id: uuid.UUID) -> uuid.UUID:
    """Return the AI conversation id for a user, creating the conversation if needed."""
    conversation = await _get_or_create_conversation(session, user_id)
    return conversation.id


async def _check_and_update_credit(session: SessionDep, user_id: uuid.UUID) -> None:
    result = await session.exec(select(AICredit).where(AICredit.user_id == user_id))
    credit = result.first()
    now = datetime.now(timezone.utc)

    if not credit:
        credit = AICredit(user_id=user_id)
        session.add(credit)
    elif credit.last_reset.date() < now.date():
        credit.used_today = 0
        credit.last_reset = now

    # if credit.used_today >= credit.daily_limit:
    #     raise ValueError("Daily AI message limit reached.")

    credit.used_today += 1



async def create_ai_message(
    session: SessionDep,
    user_id: uuid.UUID,
    topic: str,
    document_id: uuid.UUID | None = None,
) -> AIMessageResponse:
    if document_id is not None:
        document_result = await session.exec(
            select(Document).where(Document.id == document_id)
        )
        if document_result.first() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

    from app.features.ai import graph as ai_graph

    logger.info("Reached create_ai_message")
    if ai_graph.graph is None:
        raise RuntimeError("Graph not initialized. Call setup_graph() on startup.")
    conversation = await _get_or_create_conversation(session, user_id)

    try:
        logger.info("Conversation ID: %s", conversation.id)
        result = await ai_graph.graph.ainvoke(
            {
                "messages": [LangHumanMessage(content=topic)],
                "conversation_id": str(conversation.id),
                "document_id": str(document_id) if document_id else None,
            },
            config={"configurable": {"thread_id": str(conversation.id)}},
        )
        logger.debug("Raw graph result: %s", result)
        ai_text = str(result["messages"][-1].content)
    except Exception as e:
        logger.error("LLM invocation failed for user %s: %s", user_id, e)
        raise
    await _check_and_update_credit(session, user_id)
    session.add(
        AIMessage(
            conversation_id=conversation.id,
            role=AiChatRole.user,
            content=topic,
            document_id=document_id,
        )
    )
    session.add(
        AIMessage(
            conversation_id=conversation.id,
            role=AiChatRole.assistant,
            content=ai_text,
            document_id=document_id,
        )
    )
    await session.commit()

    return AIMessageResponse(message=topic, response=ai_text, document_id=document_id)


async def get_user_ai_messages(
    session: SessionDep,
    user_id: uuid.UUID,
    limit: int = 20,
    cursor: uuid.UUID | None = None,
) -> PaginatedAIMessages:
    query = (
        select(AIMessage)
        .join(AIConversation, AIMessage.conversation_id == AIConversation.id)
        .where(AIConversation.user_id == user_id)
    )

    if cursor:
        cursor_result = await session.exec(select(AIMessage).where(AIMessage.id == cursor))
        cursor_msg = cursor_result.first()
        if cursor_msg:
            query = query.where(AIMessage.created_at < cursor_msg.created_at)

    query = query.order_by(AIMessage.created_at.desc()).limit(limit + 1)

    result = await session.exec(query)
    messages = list(result.all())

    next_cursor = None
    if len(messages) > limit:
        messages = messages[:limit]
        next_cursor = messages[-1].id

    return PaginatedAIMessages(
        messages=[AIMessageRead.model_validate(m) for m in messages[::-1]],
        next_cursor=next_cursor,
    )