import logging
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain_integrations.prompt_guard_llm_wrapper import (
    PromptGuardLLMWrapper,
)
from pgchatserver.authorization import VerifyToken
from pgchatserver.intermediate_outputs import get_response
from pgchatserver.memory import build_memory
from pgchatserver.models import ChatRequest, ChatResponse
from pgchatserver.prompt_template import PROMPT_GUARD_TEMPLATE

app = FastAPI()
token_auth_scheme = HTTPBearer()
logger = logging.getLogger(__name__)


@app.post("/chat")
async def chat(
    chat_request: ChatRequest,
    bearer_token: Any = Depends(token_auth_scheme),
) -> ChatResponse:
    # Verify bearer_token
    VerifyToken(bearer_token.credentials).verify(
        required_scopes=["use:opaque-ppp-chat-bot"]
    )

    # `history` must be a list with an even number of strings,
    # because each pair of strings represents
    # a turn in the conversation. An example of a valid history is:
    # `[HUMAN_MESSAGE1, BOT_RESPONSE1, HUMAN_MESSAGE2, BOT_RESPONSE2]`.
    if (
        not isinstance(chat_request.history, list)
        or len(chat_request.history) % 2 != 0
    ):
        raise HTTPException(
            status_code=400,
            detail="history must be a list with an even number of strings",
        )

    prompt = PromptTemplate.from_template(PROMPT_GUARD_TEMPLATE)
    memory = build_memory(chat_request.history)

    if chat_request.with_intermediate_outputs:
        return get_response(
            prompt=prompt,
            memory=memory,
            input=chat_request.prompt,
            llm=OpenAI(),
        )

    """
    This is the typical case for the PromptGuard LangChain integration.
    We can get security from PromptGuard by simply wrapping the LLM,
    e.g. `llm=OpenAI()` -> `llm=PromptGuardLLMWrapper(llm=OpenAI())`.
    """
    chain = LLMChain(
        prompt=prompt,
        llm=PromptGuardLLMWrapper(llm=OpenAI()),
        memory=memory,
    )
    return ChatResponse(desanitized_response=chain.run(chat_request.prompt))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
