FROM python:3.10.12-slim-bookworm

ENV PKG_SRC_DIR /pgchatserver

RUN apt update && \
    apt upgrade -y && \
    apt install -y git

# Set up source code
COPY python-package/ $PKG_SRC_DIR
WORKDIR $PKG_SRC_DIR

# Install Python dependencies
RUN pip install -r requirements.txt

# Install chat server Python package
RUN pip install .

EXPOSE 8000

ENTRYPOINT [ "uvicorn", "src.pgchatserver.server:app", "0.0.0.0" ]
