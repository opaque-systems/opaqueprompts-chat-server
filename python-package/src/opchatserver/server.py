import logging
import os
from http import HTTPStatus
from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain.llms.opaqueprompts import OpaquePrompts
from opchatserver.authorization import VerifyToken
from opchatserver.intermediate_outputs import get_response
from opchatserver.memory import build_memory
from opchatserver.models import ChatRequest, ChatResponse
from opchatserver.prompt_template import OPAQUEPROMPTS_TEMPLATE

app = FastAPI()
token_auth_scheme = HTTPBearer()
logger = logging.getLogger(__name__)


def _get_origns() -> List[str]:
    """
    Get the origins that are allowed to make requests to the chat endpoint.

    Returns
    -------
    list of str
        The origins that are allowed to make requests to the chat endpoint.
    """
    return os.environ.get("ORIGINS", "http://localhost:3000").split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_origns(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
async def chat(
    chat_request: ChatRequest,
    bearer_token: Any = Depends(token_auth_scheme),
) -> ChatResponse:
    """
    Secure chat endpoint that uses OpaquePrompts to protect the user's privacy.

    Parameters
    ----------
    chat_request : ChatRequest
        The request body, which contains the history of the conversation
        and the prompt to be completed.
    bearer_token : Any, optional
        The bearer token, which is used to verify the user's identity.

    Returns
    -------
    ChatResponse
        The response body, which contains the bot's response to the prompt.
        If `with_intermediate_outputs` is `True`, then the response body
        also contains the intermediate outputs from OpaquePrompts and LLM.
    """
    try:
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
        prompt = PromptTemplate.from_template(OPAQUEPROMPTS_TEMPLATE)
        memory = build_memory(chat_request.history)

        if chat_request.with_intermediate_outputs:
            return get_response(
                prompt=prompt,
                memory=memory,
                input=chat_request.prompt,
                llm=OpenAI(),
            )

        # This is the typical case for the OpaquePrompts LangChain integration.
        # We can get security from OpaquePrompts by simply wrapping the LLM,
        # e.g. `llm=OpenAI()` -> `llm=OpaquePrompts(base_llm=OpenAI())`.
        chain = LLMChain(
            prompt=prompt,
            llm=OpaquePrompts(base_llm=OpenAI()),
            memory=memory,
        )
        return ChatResponse(desanitizedResponse=chain.run(chat_request.prompt))
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# Validate required env vars
if not os.environ.get("AUTH0_DOMAIN"):
    raise Exception("AUTH0_DOMAIN environment variable must be set")
if not os.environ.get("AUTH0_API_AUDIENCE"):
    raise Exception("AUTH0_API_AUDIENCE environment variable must be set")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
