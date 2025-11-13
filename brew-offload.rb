class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "https://github.com/24aft-kawasaki/homebrew-offload/archive/refs/tags/v0.0.0.tar.gz"
  sha256 "2bdc19c1d1e9ff9f682dc5e62c6f1548ee290a3fdf66f934d84bd642a55ae36d"
  license ""

  depends_on "python@3.13"

  def install
    bin.install "bin/brew-offload"
    etc.install "testenv/etc/brew-offload"
  end

  test do
    system "false"
  end
end
