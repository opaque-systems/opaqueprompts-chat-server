import uuid
from typing import List

from langchain.memory import ConversationBufferWindowMemory

UNIQUE_IDENTIFIER = str(uuid.uuid4())[:8]


def build_memory(
    history: List[str], k: int = 5, use_unique_identifier: bool = True
) -> ConversationBufferWindowMemory:
    """Build memory from history.

    Parameters
    ----------
    history : List[str]
        List of strings representing the conversation history.
    k : int, optional
        Number of turns of history to use, by default 5
    use_unique_identifier : bool, optional
        Whether to replace the human and ai prefix with a unique_identifier
        or leave them as Human and AI, by default True
    """
    if use_unique_identifier:
        memory = ConversationBufferWindowMemory(
            k=k, human_prefix=UNIQUE_IDENTIFIER, ai_prefix=UNIQUE_IDENTIFIER
        )
    else:
        memory = ConversationBufferWindowMemory(k=k)
    start_index = max(0, len(history) - 2 * k)
    for i in range(start_index, len(history) - 1, 2):
        memory.save_context(
            {"input": history[i]},
            {"output": history[i + 1]},
        )
    return memory
