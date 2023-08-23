from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    history: Optional[List[str]]
    prompt: str
    with_intermediate_outputs: bool = True


class ChatResponse(BaseModel):
    desanitized_response: str = Field(..., alias="desanitizedResponse")
    sanitized_prompt: Optional[str] = Field(None, alias="sanitizedPrompt")
    raw_response: Optional[str] = Field(None, alias="rawResponse")
