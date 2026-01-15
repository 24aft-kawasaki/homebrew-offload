class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "https://github.com/24aft-kawasaki/homebrew-offload/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "a65e15ea8fa306461c7c021bf734f24fda6a18557686f85756b25e5159735b76"
  license ""

  depends_on "python@3.13"

  def install
    bin.install "bin/brew-offload"
    etc.install "testenv/etc/brew-offload"
    etc.install "etc/brew-wrap"
    zsh_completion.install "etc/_brew-offload"
  end

  test do
    system "false"
  end
end
