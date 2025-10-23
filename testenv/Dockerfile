FROM homebrew/brew:latest

WORKDIR $HOME/testenv/

USER linuxbrew

# COPY --chown=linuxbrew ../.devcontainer/Makefile ./.devcontainer/
COPY --chown=linuxbrew ../offload ./offload/
COPY --chown=linuxbrew ../bin ./bin/
COPY --chown=linuxbrew ../etc ./etc/
COPY --chown=linuxbrew ../tests ./tests/
COPY --chown=linuxbrew ../Pipfile ./

ENV PATH="$PATH:/home/linuxbrew/.local/bin"

RUN brew install python@3.13 python@3.12 pipx \
    && pipx install pipenv \
    && pipenv install

ENTRYPOINT ["watch", "date"]
