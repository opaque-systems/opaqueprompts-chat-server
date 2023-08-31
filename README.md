# opaqueprompts-chat-server

## Description

This is a chat server that uses the [OpaquePrompts API](https://opaqueprompts.readthedocs.io/en/latest/) to demonstrate how to utilize the OpaquePrompts to build a LLM application protected by confidential computing.

To use OpaquePrompts, once you retrieve an API token from the [OpaquePrompts website](https://opaqueprompts.opaque.co), all you need to do is wrap the `llm` passed into `LLMChain` with `OpaquePrompts`:

```python
chain = LLMChain(
	prompt=prompt,
	# llm=OpenAI(),
	llm=OpaquePrompts(base_llm=OpenAI()),
	memory=memory,
)
```

You can experiment with a hosted demo on the [OpaquePrompts website](https://opaqueprompts.opaque.co). Note that the source code also includes logic for authentication and for displaying intermediate (i.e., the sanitized prompt and sanitized response) steps.