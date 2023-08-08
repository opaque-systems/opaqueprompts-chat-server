"""
This script serves as a quick demo of how one can use Sanitize and
Desanitize Chain as part of a sequential chain.
"""

from langchain.chains import SequentialChain, TransformChain

from ..desanitize_chain import DesanitizeChain  # type:ignore
from ..sanitize_chain import SanitizeChain  # type:ignore

sc1 = SanitizeChain(text_keys=["text"])
sc2 = SanitizeChain(text_keys=["chat_history", "recent_message"])

dc1 = DesanitizeChain(text_keys=["response"])
dc2 = DesanitizeChain(text_keys=["updated_chat_history", "response"])

tc1 = TransformChain(
    input_variables=["sanitized_text"],
    output_variables=["sanitized_response"],
    transform=lambda inputs: {
        "sanitized_response": "response to " + inputs["sanitized_text"]
    },
)
tc2 = TransformChain(
    input_variables=["sanitized_chat_history", "sanitized_recent_message"],
    output_variables=["sanitized_updated_chat_history", "sanitized_response"],
    transform=lambda inputs: {
        "sanitized_response": "response to "
        + inputs["sanitized_recent_message"],
        "sanitized_updated_chat_history": inputs["sanitized_chat_history"]
        + "\n"
        + inputs["sanitized_recent_message"],
    },
)

seqC1 = SequentialChain(
    chains=[sc1, tc1, dc1],
    input_variables=["text"],
    output_variables=["response"],
)
seqC2 = SequentialChain(
    chains=[sc2, tc2, dc2],
    input_variables=["chat_history", "recent_message"],
    output_variables=["updated_chat_history", "response"],
)

sample_input_1 = "hi"
sample_input_2 = {
    "chat_history": "User 1: Hi\nUser 2: Hello how are you doing?",
    "recent_message": "User 1: I am doing well, how about you?",
}

print(seqC1(sample_input_1))
print(seqC2(sample_input_2))
