## Dockerfile

### Installing
From the repo root, run:
```
docker build --file docker/Dockerfile . --tag promptguard-demo-server
```

### Running
To run the service with exposed port 8000:
```
docker run -p 8000:8000 promptguard-demo-server:latest
```

For debugging a running container:
```
docker exec -it <Container Name> /bin/bash
```

