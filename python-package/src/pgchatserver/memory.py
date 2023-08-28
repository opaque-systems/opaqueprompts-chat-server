from typing import List

from langchain.memory import ConversationBufferWindowMemory


def build_memory(
    history: List[str], k: int = 5
) -> ConversationBufferWindowMemory:
    """Build memory from history.

    Parameters
    ----------
    history : List[str]
        List of strings representing the conversation history.
    k : int, optional
        Number of turns of history to use, by default 5
    """
    memory = ConversationBufferWindowMemory(k=k)
    start_index = max(0, len(history) - 2 * k)
    for i in range(start_index, len(history) - 1, 2):
        memory.save_context(
            {"input": history[i]},
            {"output": history[i + 1]},
        )
    return memory
