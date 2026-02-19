class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "file:///tmp/homebrew-offload-0.0.1.tar.gz"
  sha256 "9f08a41c00c6bf68433c9b166607b7515fbecdfaa8028fe6da9d472b47ed9308"

  def install
    bin.install "bin/brew-offload"
    etc.install "testenv/etc/brew-offload"
    etc.install "etc/brew-wrap"
    zsh_completion.install "etc/_brew-offload"
    zsh_completion.install "etc/_brew_offload"
  end

  test do
    system "false"
  end
end
