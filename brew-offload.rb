class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "file:///tmp/homebrew-offload-0.0.1.tar.gz"
  sha256 "6b877d3067640794567496614c6bea7163228f1aecc8b675a831a7a33a198234"
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
