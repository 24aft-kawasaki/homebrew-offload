class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "https://github.com/24aft-kawasaki/homebrew-offload/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "71eca77af34526c0aa40be3e242a8e8c382e68eaa6d3215fcb9f00829366908e"
  license ""

  # Uses system Python 3.13+ - version check is performed at runtime

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
