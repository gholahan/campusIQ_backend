import logging
from contextlib import asynccontextmanager
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.core.config import LANGGRAPH_URL, OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a helpful educational assistant. "
    "Explain topics clearly and concisely to students in English. "
    "If you don't know the answer, say 'I don't know' instead of making up an answer."
)

model: Any = None
graph: Any = None
_pg_pool: AsyncConnectionPool | None = None

if OPENROUTER_API_KEY:
    model = init_chat_model(
        model="openrouter/free",
        model_provider="openai",
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )


async def _call_model(state: MessagesState) -> MessagesState:
    if model is None:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    response = await model.ainvoke(
        [
            SystemMessage(content=_SYSTEM_PROMPT),
            *state["messages"],
        ]
    )

    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chat", _call_model)
builder.set_entry_point("chat")
builder.set_finish_point("chat")


@asynccontextmanager
async def setup_graph():
    global graph, _pg_pool

    if graph is not None:
        logger.info(
            "LangGraph already initialized; saver=%s",
            getattr(graph, "saver_type", "unknown"),
        )
        yield
        return

    try:
        if LANGGRAPH_URL:
            try:
                _pg_pool = AsyncConnectionPool(
                    LANGGRAPH_URL,
                    kwargs={"prepare_threshold": None, "autocommit": True},
                    open=False,
                )
                await _pg_pool.open()

                checkpointer = AsyncPostgresSaver(_pg_pool)
                await checkpointer.setup()

                graph = builder.compile(checkpointer=checkpointer)
                graph.saver_type = type(checkpointer).__name__

                logger.info(
                    "LangGraph compiled successfully with Postgres checkpointer. Saver=%s",
                    graph.saver_type,
                )

                yield

                await _pg_pool.close()
                return

            except Exception as exc:
                logger.warning(
                    "Falling back to in-memory LangGraph checkpointer because Postgres initialization failed: %s",
                    exc,
                )

        checkpointer = MemorySaver()
        graph = builder.compile(checkpointer=checkpointer)
        graph.saver_type = type(checkpointer).__name__

        logger.info(
            "LangGraph compiled successfully with in-memory checkpointer. Saver=%s",
            graph.saver_type,
        )

        yield

    except Exception:
        logger.exception("Failed to initialize LangGraph graph.")
        raise