class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "file:///tmp/brew-offload.tar.gz"
  version "test"
  sha256 "1fd7c1c704c94dd4aa2d5c5eb7ede509414d411c6046c1ebe979b2e284485ef2"

  def build; end

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
