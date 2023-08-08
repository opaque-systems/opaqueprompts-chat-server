from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from langchain.prompts.base import BasePromptTemplate, StringPromptValue
from langchain.schema.language_model import BaseLanguageModel
from promptguard import (
    DesanitizeResponse,
    SanitizeResponse,
    desanitize,
    sanitize,
)
from pydantic import Extra


class PromptGuardChain(Chain):
    """
    A chain that uses the PromptGuard library to sanitize and desanitize
    prompts and responses.
    """

    prompt: BasePromptTemplate
    """Prompt object to use."""
    llm: BaseLanguageModel
    output_key: str = "text"  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        """Will always return text key.

        :meta private:
        """
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        return self._prompt_guard_wrapper(
            inputs, self.llm.generate_prompt, run_manager
        )

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        return self._prompt_guard_wrapper(
            inputs, self.llm.agenerate_prompt, run_manager
        )

    def _prompt_guard_wrapper(
        self,
        inputs: Dict[str, Any],
        generate_prompt_func: Callable[..., Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        inputs = self.prep_inputs(inputs)
        prompt_value_str = self.prompt.format_prompt(**inputs).to_string()
        if self.verbose:
            print("Original prompt from user", prompt_value_str)
        sanitize_response: SanitizeResponse = sanitize(prompt_value_str)
        sanitized_prompt_value_str = sanitize_response.sanitized_text
        if self.verbose:
            print("Original prompt from user", prompt_value_str)
            print("sanitizedd prompt to LLM", sanitized_prompt_value_str)
        llm_response = generate_prompt_func(
            [StringPromptValue(text=sanitized_prompt_value_str)],
            callbacks=run_manager.get_child() if run_manager else None,
        )
        desanitize_response: DesanitizeResponse = desanitize(
            llm_response.generations[0][0].text,
            secret_entropy=sanitize_response.secret_entropy,
        )
        if self.verbose:
            print("Raw response from LLM", llm_response.generations[0][0].text)
            print(
                "Desanitized response to the user",
                desanitize_response.desanitized_text,
            )
        return {self.output_key: desanitize_response.desanitized_text}

    @property
    def _chain_type(self) -> str:
        return "prompt_guard_chain"
