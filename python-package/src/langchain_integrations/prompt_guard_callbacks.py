import json
from typing import Any, Dict, List, Optional
from uuid import UUID

import langchain
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult
from promptguard import (
    DesanitizeResponse,
    SanitizeResponse,
    desanitize,
    sanitize,
)

langchain.verbose = True
langchain.debug = True


class PromptGuardCallbackHandler(BaseCallbackHandler):
    # run_id to secret_entropy
    secret_context: Dict[UUID, bytes] = dict()

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        # implement this if we would support llm level callbacks
        pass

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        # implement this if we would support llm level callbacks
        pass

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        input_str = json.dumps(inputs)
        sanitize_response: SanitizeResponse = sanitize(input_str)
        secret_entropy = sanitize_response.secret_entropy
        self.secret_context[run_id] = secret_entropy
        sanitize_inputs = json.loads(sanitize_response.sanitized_text)
        for key in inputs:
            inputs[key] = sanitize_inputs[key]

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        output_str = json.dumps(outputs)
        desanitize_response: DesanitizeResponse = desanitize(
            output_str, self.secret_context[run_id]
        )
        del self.secret_context[run_id]
        desanitized_outputs = json.loads(desanitize_response.desanitized_text)
        print(
            f"[on_chain_end] raw outputs: {outputs},\n"
            f"[on_chain_end] desanitized: {desanitized_outputs}"
        )
        print(desanitized_outputs)
        for key in outputs:
            outputs[key] = desanitized_outputs[key]
