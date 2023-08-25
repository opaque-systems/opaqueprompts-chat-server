## Dockerfile

### Installing
From the repo root, run:
```
docker build --file docker/Dockerfile . --tag promptguard-chat-server
```

Or pull the image from [GHCR](https://github.com/opaque-systems/promptguard-chat-server/pkgs/container/promptguard-chat-server):

```bash
docker pull ghcr.io/opaque-systems/promptguard-chat-server:dev
```

### Running
Before running the service, you'll need to set the following environment variables:

* `PROMPTGUARD_SERVER_HOSTNAME`: The IP address / hostname of the PromptGuard service running on ACI
* `PROMPTGUARD_SERVER_PORT`: The port of the PromptGuard service running on ACI
* `OPENAI_API_KEY`: Your OpenAI API key
* `PROMPTGUARD_API_KEY`: Your PromptGuard API key.

Then, to run the service with exposed port 8000:

```
docker run -e PROMPTGUARD_SERVER_HOSTNAME=$PROMPTGUARD_SERVER_HOSTNAME -e PROMPTGUARD_SERVER_PORT=$PROMPTGUARD_SERVER_POR
T -e OPENAI_API_KEY=$OPENAI_API_KEY -e PROMPTGUA
RD_API_KEY=$PROMPTGUARD_API_KEY -p 8000:8000 ghc
r.io/opaque-systems/promptguard-chat-server:dev
```

For debugging a running container:
```
docker exec -it <Container Name> /bin/bash
```

