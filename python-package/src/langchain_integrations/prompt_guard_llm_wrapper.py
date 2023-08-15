import logging
from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.prompts.base import StringPromptValue
from langchain.utils import get_from_dict_or_env
from pydantic import Extra, root_validator

logger = logging.getLogger(__name__)


class PromptGuardLLMWrapper(LLM):
    """
    A LLM that uses the PromptGuard library to sanitize and desanitize.


    To use, you should have the `promptguard` python package installed,
    and the environment variable `PROMPT_GUARD_ACCESS_TOKEN` set with
    your access token, or pass it as a named parameter to the constructor.

    Example:
        .. code-block:: python

            prompt_guard_llm = PromptGuardLLM(llm=ChatOpenAI())
    """

    llm: Any
    """The LLM to use."""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that the access token and python package exists
        in environment."""
        token = get_from_dict_or_env(
            values, "prompt_guard_access_token", "PROMPT_GUARD_ACCESS_TOKEN"
        )
        if token is None:
            raise ValueError(
                "Could not find PROMPT_GUARD_ACCESS_TOKEN in environment. "
                "Please set it to your PromptGuard access token."
            )
        try:
            import promptguard as pg

            assert pg.__package__ is not None
        except ImportError:
            raise ImportError(
                "Could not import promptguard python package. "
                "Please install it with `pip install promptguard`."
            )
        return values

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call out to prompt guard to do sanitization and desanitization
        before and after running LLM.
        Args:
            prompt: The prompt to pass into the model.
        Returns:
            The string generated by the model.
        Example:
            .. code-block:: python
                response = prompt_guard_llm("Tell me a joke.")
        """
        from promptguard import (
            DesanitizeResponse,
            SanitizeResponse,
            desanitize,
            sanitize,
        )

        sanitize_response: SanitizeResponse = sanitize(prompt)
        sanitized_prompt_value_str = sanitize_response.sanitized_text
        llm_response = self.llm.generate_prompt(
            [StringPromptValue(text=sanitized_prompt_value_str)],
        )
        desanitize_response: DesanitizeResponse = desanitize(
            llm_response.generations[0][0].text,
            secure_context=sanitize_response.secure_context,
        )
        return desanitize_response.desanitized_text

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "promptguard"
