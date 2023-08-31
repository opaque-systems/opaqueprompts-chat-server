# opaqueprompts-chat-server

## Description

This is a chat server that uses the [OpaquePrompts API](https://opaqueprompts.readthedocs.io/en/latest/) to build a LLM application protected by confidential computing. OpaquePrompts is a privacy layer around LLMs that hides sensitive data from the model provider. You can find a deployed version of this chat server on the [OpaquePrompts website (https://opaqueprompts.opaque.co).

## OpaquePrompts LangChain Integration

This application is built with [OpaquePrompts LangChain integration](https://python.langchain.com/docs/integrations/llms/opaqueprompts).

To use OpaquePrompts, once you retrieve an API token from the [OpaquePrompts website](https://opaqueprompts.opaque.co), all you need to do is wrap the `llm` passed into `LLMChain` with `OpaquePrompts`:

```python
chain = LLMChain(
	prompt=prompt,
	# llm=OpenAI(),
	llm=OpaquePrompts(base_llm=OpenAI()),
	memory=memory,
)
```

Note that the source code also includes logic for authentication and for displaying intermediate (i.e., the sanitized prompt and sanitized response) steps.