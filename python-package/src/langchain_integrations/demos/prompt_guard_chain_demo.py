from langchain.callbacks.stdout import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.prompt import PromptTemplate

from ..prompt_guard_chain import PromptGuardChain

prompt_template = """
As an AI assisant, you will answer questions according to given context.
Important PII data is encrypted in both context and question.
You must treat the encrypted data as opaque strings and can use them as meaning
entities in the response.
Different encrypted items could be the same entity based on the semantics.
Conversation History: ```{history}```
Context : ```Mr. Carl Smith is a 31-year-old man who has been experiencing
homelessness on and off for all his adult life. Mr. Smith says he is about
5’5” and weighs approximately 129 lbs. He presents as
very thin, typically wearing a clean white undershirt
and loose-fitting khaki shorts at interviews.
His brown hair is disheveled and dirty looking, and
he constantly fidgets and shakes his hand or
knee during interviews. Despite his best efforts, Carl is a poor historian. ```
Question: ```{question}```

"""

chain = PromptGuardChain(
    prompt=PromptTemplate.from_template(prompt_template),
    llm=ChatOpenAI(),
    memory=ConversationBufferWindowMemory(k=2),
    verbose=True,
)


print(
    chain.run(
        {"question": """How high is he? """},
        callbacks=[StdOutCallbackHandler()],
    )
)

print(
    chain.run(
        {"question": """What is the weight for him? """},
        callbacks=[StdOutCallbackHandler()],
    )
)
