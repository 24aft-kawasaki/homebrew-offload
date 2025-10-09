FROM homebrew/brew:latest

WORKDIR $HOME/testenv/

COPY ../.devcontainer/Makefile ./.devcontainer/
COPY ../offload ./offload/
COPY ../bin ./bin/
COPY ../etc ./etc/
COPY ../tests ./tests/
COPY ../Pipfile ./


RUN brew install python@3.13 python@3.12

ENTRYPOINT ["/bin/bash"]
