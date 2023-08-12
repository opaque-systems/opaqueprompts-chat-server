from typing import Any, List, Optional

import langchain
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

langchain.verbose = True
langchain.debug = True


class EchoLLM(LLM):
    """Echo LLM wrapper for testing purposes.
    The LLM will return the prompt as the response.
    """

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "echo"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        return "llm response"
