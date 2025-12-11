PYTHON_VERSION:=3.13
PATH:=${PATH}:/home/linuxbrew/.linuxbrew/bin

HOMEBREW_PREFIX:=/home/linuxbrew/.linuxbrew

localWorkspaceFolder:=/workspaces/homebrew-offload

all: install-brew install-python link-brew-offload-config-file set-path-to-brew-offload

install-brew:
	yes | /bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	echo >> ${HOME}/.bashrc
	echo 'eval "$$(${HOMEBREW_PREFIX}/bin/brew shellenv)"' >> ${HOME}/.bashrc

install-python:
	brew install python@${PYTHON_VERSION} pipx
	pipx install pipenv
	echo $$(brew --prefix)
	pipenv sync --dev

link-brew-offload-config-file:
	mkdir -p ${HOMEBREW_PREFIX}/etc/brew-offload
	test -n "${localWorkspaceFolder}"
	ln -s ${localWorkspaceFolder}/testenv/etc/brew-offload/config.json ${HOMEBREW_PREFIX}/etc/brew-offload/config.json

set-path-to-brew-offload:
	echo 'export PATH="$${PATH}:${localWorkspaceFolder}/bin"' >> $$HOME/.bashrc
