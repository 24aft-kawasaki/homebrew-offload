PYTHON_VERSION:=3.13
PATH:=${PATH}:/home/linuxbrew/.linuxbrew/bin

install-brew:
	yes | /bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	echo >> /home/codespace/.bashrc
	echo 'eval "$$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/codespace/.bashrc

install-python:
	brew install python@${PYTHON_VERSION}
	pipenv sync --dev
