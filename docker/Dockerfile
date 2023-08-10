FROM python:3.10.12-slim-bookworm

ENV PKG_SRC_DIR /pgdemoserver

# Set up source code
COPY python-package/ $PKG_SRC_DIR
WORKDIR $PKG_SRC_DIR

# Install Python package
RUN pip install -r requirements.txt
RUN pip install .

EXPOSE 8000

ENTRYPOINT [ "uvicorn", "src.pgdemoserver.server:app" ]
