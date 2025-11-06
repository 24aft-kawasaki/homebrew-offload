FROM homebrew/brew:latest

ENV HOME=/home/linuxbrew

WORKDIR $HOME/testenv/

ENV PATH="$PATH:/home/linuxbrew/.local/bin:$HOME/testenv/bin"

RUN brew install python@3.13 python@3.12 pipx \
    && pipx install pipenv \
    && mkdir ~/.offload

COPY --chown=linuxbrew ../bin ./bin/
COPY --chown=linuxbrew ../etc ./etc/
COPY --chown=linuxbrew ../tests ./tests/
COPY --chown=linuxbrew ../Pipfile ./

COPY --chown=linuxbrew ./testenv/etc ./etc/

RUN sudo mkdir -p /etc/brew-offload \
    && sudo ln -s ${HOME}/testenv/etc/brew-offload/config.json /etc/brew-offload/config.json \
    && sudo chown -h linuxbrew:linuxbrew /etc/brew-offload/config.json

ENTRYPOINT ["tail", "-f", "/dev/null"]
