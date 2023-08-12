import langchain_integrations.prompt_guard_funcs as pgf
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
    get intermediate output chain

    Parameters
    ----------
    prompt : ChatPromptTemplate
        the prompt template used by the chain
    llm : LLM
        the llm used by the chain

    Returns
    -------
    RunnableSequence
        the intermediate output chain
    """
    pg_chain: RunnableSequence = (
        RunnableMap(
            {
                "inputs_after_sanitize": (lambda x: pgf.sanitize(x)),
            }
        )
        | RunnableMap(
            {
                "sanitized_prompt": (
                    lambda x: x["inputs_after_sanitize"]["sanitized_input"][
                        "prompt"
                    ]
                ),
                "raw_response": (
                    lambda x: x["inputs_after_sanitize"]["sanitized_input"]
                )
                | prompt
                | llm
                | StrOutputParser(),
                "secure_context": (
                    lambda x: x["inputs_after_sanitize"]["secure_context"]
                ),
            }
        )
        | RunnableMap(
            {
                "sanitized_prompt": (lambda x: x["sanitized_prompt"]),
                "raw_response": (lambda x: x["raw_response"]),
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
    get chat response with intermediate outputs

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
        the chat response with intermediate outputs
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
