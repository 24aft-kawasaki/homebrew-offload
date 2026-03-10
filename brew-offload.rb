class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "https://github.com/24aft-kawasaki/homebrew-offload/archive/refs/tags/v0.4.0-test.tar.gz"
  sha256 "5db1474d0b3fae3ca9956731269e9c787c99a4b178e1ffcc04da264eec4f3779"
  license ""

  # Uses system Python 3.14+ - version check is performed at runtime

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
