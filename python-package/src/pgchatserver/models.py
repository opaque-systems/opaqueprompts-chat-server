from pydantic import BaseModel


class ChatRequest(BaseModel):
    history: list[str]


class ChatResponse(BaseModel):
    sanitized_prompt: str
    raw_response: str
    desanitized_response: str
