class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "https://github.com/24aft-kawasaki/homebrew-offload/archive/refs/tags/v1.2.3-test.tar.gz"
  sha256 "d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed"
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
