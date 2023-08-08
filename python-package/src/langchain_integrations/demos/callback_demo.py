import langchain
from langchain.chains import LLMChain, SequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

from ..prompt_guard_callbacks import PromptGuardCallbackHandler

langchain.verbose = True
langchain.debug = True


# This is an LLMChain to write a synopsis given a title
# of a play and the era it is set in.
llm = OpenAI(temperature=0.7)
template = """You are a playwright. Given the title of play,
the era and the context it is set in, it is your job to write
a synopsis for that title.
Important PII data is encrypted in both context and question.
You must treat the encrypted data as opaque strings and can use them as meaning
entities in the response.
Different encrypted items could be the same entity based on the semantics.
The encrypted item has the format of
OPAQUEPPPTAGSTART_<type>_<data>_OPAQUEPPPTAGEND.
You must make sure to preserve the format and the data inside the tag.
Any response that does not preserve the format and the data inside the tag
will be rejected.
You shouldn't craft new items following the format.
You should only use the items
provided in the context and question.

Title: {title}
Era: {era}
Context: {context}
Playwright: This is a synopsis for the above play:"""
prompt_template = PromptTemplate(
    input_variables=["title", "era", "context"], template=template
)
synopsis_chain = LLMChain(
    llm=llm, prompt=prompt_template, output_key="synopsis"
)


# This is an LLMChain to write a review of a play given a synopsis.
llm = OpenAI(temperature=0.7)
template = """You are a play critic from the New York Times.
Given the synopsis of play, it is your job to write a review for that play.
Important PII data is encrypted in both context and question.
You must treat the encrypted data as opaque strings and can use them as meaning
entities in the response.
Different encrypted items could be the same entity based on the semantics.
Encrypted items have a format
`OPAQUEPPPTAGSTART_<type>_<data>_OPAQUEPPPTAGEND`.
You must make sure to preserve the format and the data inside the tag.
Any response that does not preserve the format and the data inside the
tag will be rejected.
You shouldn't craft new items following the format.
You should only use the items provided in the context and question.

Play Synopsis:
{synopsis}
Review from a New York Times play critic of the above play:"""
prompt_template = PromptTemplate(
    input_variables=["synopsis"], template=template
)
review_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="review")


# This is the overall chain where we run these two chains in sequence.
overall_chain = SequentialChain(
    chains=[synopsis_chain, review_chain],
    input_variables=["era", "title", "context"],
    # Here we return multiple variables
    output_variables=["synopsis", "review"],
    verbose=True,
    callbacks=[PromptGuardCallbackHandler()],
)


overall_chain(
    {
        "title": "Tragedy at sunset on the beach",
        "era": "Victorian England",
        "context": """Mr. Carl Smith is a 31-year-old man who has
been experiencing homelessness on and off for all
his adult life. Mr. Smith says he is about 5’5” and
weighs approximately 129 lbs. He presents as
very thin, typically wearing a clean white undershirt and
loose-fitting khaki shorts at interviews.
His brown hair is disheveled and dirty looking, and he
constantly fidgets and shakes his hand or
knee during interviews. Despite his best efforts,
Carl is a poor historian. In interviews with this
writer, he needed constant redirecting and prompting to
provide information about his
personal and psychiatric history. Carl is diagnosed with
Major Depressive Disorder; recurrent,
Anxiety Disorder, Attention Deficit Hyperactivity Disorder,
Intermittent Explosive Disorder, and
a possible traumatic brain injury. Physically, he has degenerative
disc disease, Lumbar radiculopathy, Allergic Rhinitis, and a history of
fainting since childhood. When asked why
working is difficult for him, Carl responded
“I have a hard time controlling myself. When I get
stressed out, I immediately shut down.”
""",
    }
)
