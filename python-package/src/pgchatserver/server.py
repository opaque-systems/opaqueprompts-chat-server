import logging
import os
from typing import Any, Union

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain_integrations.prompt_guard_llm_wrapper import (
    PromptGuardLLMWrapper,
)
from pgchatserver.authorization import VerifyToken
from pgchatserver.echo_llm import EchoLLM
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
) -> Union[ChatResponse, str]:
    logger.info("chat_request: %s", chat_request)
    # Verify bearer_token
    VerifyToken(bearer_token.credentials).verify(
        required_scopes=["use:opaque-ppp-chat-bot"]
    )

    if not isinstance(chat_request.history, list):
        raise HTTPException(
            status_code=400, detail="history must be a list of strings"
        )
    if len(chat_request.history) % 2 != 1:
        raise HTTPException(
            status_code=400,
            detail="history must have an odd number of strings",
        )

    prompt = PromptTemplate.from_template(PROMPT_GUARD_TEMPLATE)
    memory = build_memory(chat_request.history)
    if os.environ.get("TEST_WITH_ECHO_LLM"):
        llm = EchoLLM()
    else:
        llm = OpenAI()

    if os.environ.get("SKIP_INTERMEIDATE_OUTPUTS"):
        """
        This is the typical case for LangChain integration.
        We can get security from PromptGuard by simply wrapping the LLM.
        e.g. `llm=OpenAI()` -> `llm=PromptGuardLLMWrapper(llm=OpenAI())`
        """
        chain = LLMChain(
            prompt=prompt,
            llm=PromptGuardLLMWrapper(llm=llm),
            memory=memory,
        )
        return chain.run(chat_request.history[-1])

    return get_response(
        prompt=prompt, memory=memory, input=chat_request.history[-1], llm=llm
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
