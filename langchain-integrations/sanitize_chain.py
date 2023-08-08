from langchain.chains import SequentialChain, TransformChain
from langchain.chains.base import Chain
import promptguard as pg
from typing import Callable, Dict, List, Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
import uuid


class SanitizeChain(Chain):
    
    text_keys: List[str] = ["text"]
    """The keys expected by the SanitizeChains's input dictionary. The output dictionary will
    have the same keys, this time with the sanitized context of the input dictionary.
    """
    
    CONTEXT_KEY: str = "promptguard_context"
    
    def convert_key_name(key: str) -> str:
        return "sanitized_"+key
    
    @property
    def input_keys(self) -> List[str]:
        """Expect input keys.

        :meta private:
        """
        return self.text_keys

    @property
    def output_keys(self) -> List[str]:
        """Return output keys.

        :meta private:
        """
        return [SanitizeChain.convert_key_name(key) for key in self.text_keys] + [self.CONTEXT_KEY]
    
    
    def _call(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """Execute the chain.

        This is a private method that is not user-facing. It is only called within
            `Chain.__call__`, which is the user-facing wrapper method that handles
            callbacks configuration and some input/output processing.

        Args:
            inputs: A dict of named inputs to the chain. Assumed to contain all inputs
                specified in `Chain.input_keys`, including any inputs added by memory.
            run_manager: The callbacks manager that contains the callback handlers for
                this run of the chain.

        Returns:
            A dict of named outputs. Should contain all outputs specified in
                `Chain.output_keys`.
        """
        divider = str(uuid.uuid4())
        plaintext_string = ""
        for key in self.text_keys:
            plaintext_string += inputs[key]
            plaintext_string += divider
        sanitize_response = pg.sanitize(plaintext_string)
        outputs = {self.CONTEXT_KEY: sanitize_response.secret_entropy}
        split_sanitized_text = sanitize_response.sanitized_text.split(divider)
        for i, key in enumerate(self.text_keys):
            outputs[SanitizeChain.convert_key_name(key)] = split_sanitized_text[i]
        return outputs