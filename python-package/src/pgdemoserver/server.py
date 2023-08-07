# main.py

from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    chat_history: str
    plaintext_prompt: str


class ChatResponse(BaseModel):
    anonymized_prompt: str
    plaintext_response: str
    updated_chat_history: str


@app.post("/chat/")
async def chat(
    chat_request: ChatRequest,
    bearer_token: Annotated[str | None, Header()] = None,
) -> ChatResponse:
    # TODO(ENG-1759): Implement

    return ChatResponse(
        anonymized_prompt="TODO",
        plaintext_response="TODO",
        updated_chat_history="TODO",
    )
