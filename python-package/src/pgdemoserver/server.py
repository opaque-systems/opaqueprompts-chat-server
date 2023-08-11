# main.py

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from pgdemoserver.authorization import VerifyToken
from pydantic import BaseModel

# from pgdemoserver.authorization import token_validator

app = FastAPI()
token_auth_scheme = HTTPBearer()


class ChatRequest(BaseModel):
    chat_history: str
    plaintext_prompt: str


class ChatResponse(BaseModel):
    sanitized_prompt: str
    sanitized_response: str
    plaintext_response: str
    # Unsure if we need this updated_chat_history, seems the easiest way
    # to ensure it is sent in the right format for the next request
    # but should confirm with frontend.
    updated_chat_history: str


@app.post("/chat/")
async def chat(
    chat_request: ChatRequest,
    bearer_token: Any = Depends(token_auth_scheme),
) -> ChatResponse:
    # Verify bearer_token
    VerifyToken(bearer_token.credentials).verify(
        required_scopes=["use:opaque-ppp-chat-bot"]
    )
    # TODO(ENG-1759): Implement

    return ChatResponse(
        sanitized_prompt="TODO",
        sanitized_response="TODO",
        plaintext_response="TODO",
        updated_chat_history="TODO",
    )
