from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    history: Optional[list[str]]
    prompt: str
    with_intermediate_outputs: bool = True


class ChatResponse(BaseModel):
    desanitized_response: str
    sanitized_prompt: Optional[str]
    raw_response: Optional[str]
