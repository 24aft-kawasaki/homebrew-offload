PYTHON_VERSION:=3.14
PATH:=${PATH}:${HOME}/.local/bin:/home/linuxbrew/.linuxbrew/bin
SHELL:=/bin/bash

HOMEBREW_PREFIX:=/home/linuxbrew/.linuxbrew

localWorkspaceFolder?=${GITHUB_WORKSPACE}

all: install-brew install-python link-brew-offload-config-file set-path-to-brew-offload

install-brew:
	yes | /bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	echo >> ${HOME}/.bashrc
	echo 'eval "$$(${HOMEBREW_PREFIX}/bin/brew shellenv)"' >> ${HOME}/.bashrc

install-python: install-brew
	brew install python@${PYTHON_VERSION} pipx
	pipx install pipenv
	echo $$(brew --prefix)
	pipx ensurepath
	${SHELL} -c 'pipenv sync --dev'

link-brew-offload-config-file: install-brew
	mkdir -p $$(brew --prefix)/etc/brew-offload
	test -n "${localWorkspaceFolder}"
	ln -s ${localWorkspaceFolder}/testenv/etc/brew-offload/config.json $$(brew --prefix)/etc/brew-offload/config.json

set-path-to-brew-offload:
	echo 'export PATH="$${PATH}:${localWorkspaceFolder}/bin"' >> $$HOME/.bashrc
