import uuid
from typing import Dict, List, Optional

import promptguard as pg
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain


class DesanitizeChain(Chain):
    text_keys: List[str] = ["text"]
    """The keys output by the DesanitizeChain's input dictionary. The input
    dictionary will have the same keys, with _sanitize prepended to the front
    of them.
    """

    CONTEXT_KEY: str = "promptguard_context"

    def convert_key_name(key: str) -> str:
        return "sanitized_" + key

    @property
    def input_keys(self) -> List[str]:
        """Expect input keys.

        :meta private:
        """
        return [
            DesanitizeChain.convert_key_name(key) for key in self.text_keys
        ] + [self.CONTEXT_KEY]

    @property
    def output_keys(self) -> List[str]:
        """Return output keys.

        :meta private:
        """
        return self.text_keys

    def _call(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """Execute the chain.

        This is a private method that is not user-facing. It is only called
            within `Chain.__call__`, which is the user-facing wrapper method
            that handles callbacks configuration and some input/output
            processing.

        Args:
            inputs: A dict of named inputs to the chain. Assumed to contain
                all inputs specified in `Chain.input_keys`, including any
                inputs added by memory.
            run_manager: The callbacks manager that contains the callback
                handlers for this run of the chain.

        Returns:
            A dict of named outputs. Should contain all outputs specified in
                `Chain.output_keys`.
        """
        divider = str(uuid.uuid4())
        plaintext_string = ""
        for key in self.text_keys:
            plaintext_string += inputs[DesanitizeChain.convert_key_name(key)]
            plaintext_string += divider
        desanitize_response = pg.desanitize(
            plaintext_string, inputs[self.CONTEXT_KEY]
        )
        outputs = {}
        split_sanitized_text = desanitize_response.desanitized_text.split(
            divider
        )
        for i, key in enumerate(self.text_keys):
            outputs[key] = split_sanitized_text[i]
        return outputs
