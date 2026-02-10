class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "https://github.com/24aft-kawasaki/homebrew-offload/archive/refs/tags/v0.2.1.tar.gz"
  sha256 "940a32298d181835ca9b10ace3ce2460326480be9a79c67e6cb35a15b658b207"
  license ""

  # Uses system Python 3.9+ - version check is performed at runtime

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
