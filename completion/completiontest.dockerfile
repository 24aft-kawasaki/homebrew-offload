FROM homebrew/brew:latest

SHELL ["/bin/bash", "-c"]

RUN << 'EOF'
set -Eeuo pipefail

brew install zsh zsh-completions
cat << 'EOT' >> ~/.zshrc
if type brew &>/dev/null; then
    FPATH=$(brew --prefix)/share/zsh-completions:$FPATH

    autoload -Uz compinit
    compinit
fi
EOT
brew --version
EOF
