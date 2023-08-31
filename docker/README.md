## Dockerfile

### Installing
From the repo root, run:
```
docker build --file docker/Dockerfile . --tag opaqueprompts-chat-server
```

Or pull the image from [GHCR](https://github.com/opaque-systems/opaqueprompts-chat-server/pkgs/container/opaqueprompts-chat-server):

```bash
docker pull ghcr.io/opaque-systems/opaqueprompts-chat-server:dev
```

### Running
Before running the service, you'll need to set the following environment variables:

* `OPAQUEPROMPTS_SERVER_HOSTNAME`: The IP address / hostname of the OpaquePrompts service running on ACI
* `OPAQUEPROMPTS_SERVER_PORT`: The port of the OpaquePrompts service running on ACI
* `OPENAI_API_KEY`: Your OpenAI API key
* `OPAQUEPROMPTS_API_KEY`: Your OpaquePrompts API key.

Then, to run the service with exposed port 8000:

```
docker run -e OPAQUEPROMPTS_SERVER_HOSTNAME=$OPAQUEPROMPTS_SERVER_HOSTNAME -e OPAQUEPROMPTS_SERVER_PORT=$OPAQUEPROMPTS_SERVER_PORT -e OPENAI_API_KEY=$OPENAI_API_KEY -e OPAQUEPROMPTS_API_KEY=$OPAQUEPROMPTS_API_KEY -p 8000:8000 ghcr.io/opaque-systems/opaqueprompts-chat-server:dev
```

Alternatively, you can set the environment variables in a file and [pass that file in with `--env-file`](https://docs.docker.com/engine/reference/commandline/run/#env).

For debugging a running container:
```
docker exec -it <Container Name> /bin/bash
```

