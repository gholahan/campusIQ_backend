import logging
from contextlib import asynccontextmanager
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.core.config import LANGGRAPH_URL, OPENROUTER_API_KEY
from app.core.tool_gate import requires_forced_retrieval
from app.features.ai.state import SYSTEM_PROMPT, ChatState
from app.features.ai.tools import tools


logger = logging.getLogger(__name__)


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


if model is not None:
    model_with_tools = model.bind_tools(tools)
else:
    model_with_tools = None


async def _build_checkpointer():
    if LANGGRAPH_URL:
        try:
            _pg_pool = AsyncConnectionPool(
                LANGGRAPH_URL,
                kwargs={
                    "prepare_threshold": None,
                    "autocommit": True,
                },
                open=False,
                reconnect_timeout=5,
                check=AsyncConnectionPool.check_connection,
            )
            await _pg_pool.open()
            checkpointer = AsyncPostgresSaver(_pg_pool)
            await checkpointer.setup()
            return checkpointer, _pg_pool
        except Exception as exc:
            logger.warning(
                "Falling back to in-memory LangGraph checkpointer because Postgres initialization failed: %s",
                exc,
            )
    return MemorySaver(), None


# CHAT NODE

async def _call_model(
    state: ChatState,
) -> ChatState:

    if model_with_tools is None:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured"
        )

    messages = state["messages"]
    document_id = state.get("document_id")
    last_message = messages[-1] if messages else None
    is_human_turn = last_message is not None and getattr(last_message, "type", None) == "human"

    forced = is_human_turn and (
        document_id is not None or requires_forced_retrieval(last_message.content)
    )

    if document_id and is_human_turn:
        scoped_suffix = (
            "\n\nThe user is asking about a specific document (document_id: "
            f"{document_id}). "
            "You MUST call search_document first. "
            "Base your answer ONLY on what the tool returns — "
            "do not blend in anything from earlier in this conversation."
        )
        system_prompt = SYSTEM_PROMPT + scoped_suffix
    else:
        system_prompt = SYSTEM_PROMPT

    invoker = model_with_tools.bind(tool_choice="required") if forced else model_with_tools
    response = await invoker.ainvoke(
        [
            SystemMessage(content=system_prompt),
            *messages,
        ]
    )

    return {
        "conversation_id": state["conversation_id"],
        "document_id": document_id if is_human_turn else None,
        "messages": [response],
    }


# GRAPH
builder = StateGraph(ChatState)

builder.add_node("chat", _call_model,)

builder.add_node("tools",ToolNode(tools))

builder.set_entry_point("chat")

builder.add_conditional_edges("chat", tools_condition,)

builder.add_edge("tools", "chat")

builder.set_finish_point("chat")


@asynccontextmanager
async def setup_graph():

    global graph, _pg_pool

    if graph is not None:

        logger.info(
            "LangGraph already initialized; saver=%s",
            getattr(
                graph,
                "saver_type",
                "unknown",
            ),
        )

        yield
        return

    try:
        checkpointer, _pg_pool = await _build_checkpointer()

        graph = builder.compile(checkpointer=checkpointer)

        graph.saver_type = type(checkpointer).__name__

        logger.info(
            "LangGraph compiled successfully with %s checkpointer.",
            graph.saver_type,
        )

        yield

        if _pg_pool is not None:
            await _pg_pool.close()

        return

    except Exception:

        logger.exception(
            "Failed to initialize LangGraph graph."
        )

        raise