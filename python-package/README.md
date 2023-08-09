### Promptguard demo server

A simple HTTP server based on FastAPI used to interact with the `promptguard` python package.

## Running the server
Run the server using `uvicorn`:
```
uvicorn --app-dir src/pgdemoserver server:app --reload
```
This will spin it up on localhost:8000. To see the API docs generated automatically, go to localhost:8000/docs (OpenAPI) or localhost:8000/redocs (ReDoc).
