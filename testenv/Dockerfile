FROM homebrew/brew:latest

ENV HOME=/home/linuxbrew
ENV HOMEBREW_PREFIX=/home/linuxbrew/.linuxbrew

WORKDIR $HOME/testenv/

ENV PATH="$PATH:/home/linuxbrew/.local/bin:$HOME/testenv/bin"

RUN brew install python@3.13 python@3.12 pipx \
    && pipx install pipenv \
    && mkdir ~/.offload

COPY --chown=linuxbrew bin/        ./bin/
COPY --chown=linuxbrew etc/        ./etc/
COPY --chown=linuxbrew Pipfile     ./
COPY --chown=linuxbrew testenv/etc ./etc/

RUN mkdir -p ${HOMEBREW_PREFIX}/etc/brew-offload \
    && chown linuxbrew ${HOMEBREW_PREFIX}/etc/brew-offload \
    && ln -s ${HOME}/testenv/etc/brew-offload/config.json ${HOMEBREW_PREFIX}/etc/brew-offload/config.json \
    && chown linuxbrew ${HOMEBREW_PREFIX}/etc/brew-offload/config.json

ENTRYPOINT ["tail", "-f", "/dev/null"]
