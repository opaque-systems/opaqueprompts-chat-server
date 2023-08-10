from typing import Any, List, Optional

import langchain
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableMap

from .. import prompt_guard_funcs as pgf

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
        return prompt


context = """
Mr. Carl Smith is a 31-year-old man who has been experiencing
homelessness on and off for all his adult life. Mr. Smith says he is about
5’5” and weighs approximately 129 lbs. He presents as
very thin, typically wearing a clean white undershirt
and loose-fitting khaki shorts at interviews.
His brown hair is disheveled and dirty looking, and
he constantly fidgets and shakes his hand or
knee during interviews. Despite his best efforts, Carl is a poor historian.
"""

template = """Answer the question based only on the following context:
{context}

Question: {question}

Answer:
"""


prompt = ChatPromptTemplate.from_template(template)
llm = EchoLLM()

chain = (
    pgf.sanitize
    | RunnableMap(
        {
            "response": (lambda x: x["sanitized_input"])
            | prompt
            | llm
            | StrOutputParser(),
            "secure_context": lambda x: x["secure_context"],
        }
    )
    | (lambda x: pgf.desanitize(x["response"], x["secure_context"]))
)

chain.invoke({"question": "How high is he?", "context": context})
