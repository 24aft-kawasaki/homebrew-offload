class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "https://github.com/24aft-kawasaki/homebrew-offload/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "4020f13de836c8dc1bc814352a9ad149868547729137c4e7a66d28e194cd9734"
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
