import langchain.utilities.promptguard as pgf
from langchain.llms.base import LLM
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BasePromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableMap, RunnableSequence
from pgchatserver.models import ChatResponse


def get_intermediate_output_chain(
    prompt: ChatPromptTemplate, llm: LLM
) -> RunnableSequence:
    """
    Build and return a chain that can give intermediate outputs, using
    the LangChain expression language. It uses sanitize() and desanitize()
    from the prompt guard functions to avoid leaking senitive information
    to the llm.

    This is used by the chat server to get intermediate outputs, which is
    not a general use case of prompt guard. For a simpler usage of prompt
    guard, please see `PromptGuardLLMWrapper`.

    Parameters
    ----------
    prompt : ChatPromptTemplate
        the prompt template used by the chain
    llm : LLM
        the llm used by the chain

    Returns
    -------
    RunnableSequence
        the chain that can give intermediate outputs including
        `sanitized_prompt`, `raw_response`, `desanitized_response`.

        `sanitized_prompt` is the prompt after sanitization.
        `raw_response` is the raw response from the llm.
        `desanitized_response` is the response after desanitization.
    """
    pg_chain: RunnableSequence = (
        RunnableMap(
            {
                # sanitize the input
                "inputs_after_sanitize": (lambda x: pgf.sanitize(x)),
            }
        )
        | RunnableMap(
            {
                # get the sanitized prompt
                "sanitized_prompt": (
                    lambda x: x["inputs_after_sanitize"]["sanitized_input"][
                        "prompt"
                    ]
                ),
                # pass the sanitized input to the llm and get the raw response
                "raw_response": (
                    lambda x: x["inputs_after_sanitize"]["sanitized_input"]
                )
                | prompt
                | llm
                | StrOutputParser(),
                # pass through the secure context from the sanitized input
                "secure_context": (
                    lambda x: x["inputs_after_sanitize"]["secure_context"]
                ),
            }
        )
        | RunnableMap(
            {
                "sanitized_prompt": (lambda x: x["sanitized_prompt"]),
                "raw_response": (lambda x: x["raw_response"]),
                # desanitize the response
                "desanitized_response": (
                    lambda x: pgf.desanitize(
                        x["raw_response"],
                        x["secure_context"],
                    )
                ),
            }
        )
    )
    return pg_chain


def get_response(
    prompt: BasePromptTemplate,
    memory: ConversationBufferWindowMemory,
    input: str,
    llm: LLM,
) -> ChatResponse:
    """
    Get chat response with intermediate outputs

    Parameters
    ----------
    prompt : BasePromptTemplate
        the prompt template used by the chain
    memory : ConversationBufferWindowMemory
        memory that stores the conversation history
    input : str
        the user input message
    llm : LLM
        the llm used by the chain

    Returns
    -------
    ChatResponse
        the chat response with intermediate outputs including
        `sanitized_prompt`, `raw_response`, `desanitized_response`.

        `sanitized_prompt` is the prompt after sanitization.
        `raw_response` is the raw response from the llm.
        `desanitized_response` is the response after desanitization.
    """
    pg_chain = get_intermediate_output_chain(prompt, llm=llm)
    return ChatResponse(
        **pg_chain.invoke(
            {
                "prompt": input,
                "history": memory.load_memory_variables({})["history"],
            }
        )
    )
