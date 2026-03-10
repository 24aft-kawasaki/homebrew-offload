class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "file:///tmp/homebrew-offload-0.0.1.tar.gz"
  sha256 "784d7ae7fa4eca009748779fc5fe144062f94bfd712bfbf6c813bd50b399ea20"
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
