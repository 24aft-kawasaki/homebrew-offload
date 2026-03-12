class BrewOffload < Formula
  desc "Homebrew wrapper to offload some formulae"
  homepage "https://github.com/24aft-kawasaki/homebrew-offload"
  url "file:///tmp/homebrew-offload-0.0.1.tar.gz"
  sha256 "6bb6a9c38c0c64db049c6ac30e2a1b29c0a3c177c653a49813338641ed29d68c"
  license ""

  # Uses system Python 3.14+ - version check is performed at runtime

  def install
    libexec.install Dir["bin/*"]
    (bin/"brew-offload").write_env_script libexec/"brew-offload",
      :PATH => "$PATH:#{Formula["python@3.14"].opt_bin}"
    etc.install "testenv/etc/brew-offload"
    (etc/"brew-offload").install "etc/brew-wrap"
    zsh_completion.install "etc/_brew-offload"
    zsh_completion.install "etc/_brew_offload"
  end

  test do
    system "false"
  end
end
