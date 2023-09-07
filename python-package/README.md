### OpaquePrompts chat server

A simple HTTP server based on FastAPI used to interact with the `opaqueprompts` python package.

## Running the server
Run the server using `uvicorn`:

```
uvicorn --app-dir src/opchatserver server:app --reload --host 0.0.0.0
```
This will spin it up on localhost:8000. To see the API docs generated automatically, go to localhost:8000/docs (OpenAPI) or localhost:8000/redocs (ReDoc).


## ENV variables

There are a few environment variables that can be set to configure the server:

- `ORIGINS` - a comma-separated list of origins to allow CORS requests from. For example, `http://localhost:3000,http://localhost:8000` will allow requests from the local development server and from the server itself. Defaults to `http://localhost:3000`.

- `OPENAI_MODEL` - the name of the OpenAI model to use. For example, `gpt-3.5-turbo` or `gpt-4`. Defaults to `gpt-3.5-turbo`.
