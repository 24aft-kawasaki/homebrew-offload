class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "https://github.com/24aft-kawasaki/homebrew-offload/archive/refs/tags/v0.4.0-test.tar.gz"
  sha256 "8679f470b70e562144a9c6fd18a25efbd0541594bb5ae7dbfe5b65c6f5fe5156"
  license ""

  # Uses system Python 3.9+ - version check is performed at runtime

  def install
    bin.install "bin/brew-offload"
    etc.install "testenv/etc/brew-offload"
    (etc/"brew-offload").install "etc/brew-wrap"
    zsh_completion.install "etc/_brew-offload"
    zsh_completion.install "etc/_brew_offload"
  end

  test do
    system "false"
  end
end
