# Brew-offload

**Brew-offload** is a wrapper around [Homebrew](https://brew.sh) that helps you manage disk space efficiently by offloading large formulae to other directories or external storage.

---

## Overview

As your Homebrew installation grows, it can quickly consume significant disk space—especially with large packages and dependencies. **Brew-offload** addresses this issue by automatically relocating selected formulae to configurable or external storage, keeping your main drive clean without disrupting your normal Homebrew workflow.

---

## Key Features

Key highlights include:

- 🚀 **Seamless Integration** – Functions as a transparent Homebrew wrapper. Your usual `brew` commands continue to work as expected.
- 💾 **Storage Optimization** – Offload large formulae to any location, including external drives.
- ⚙️ **Configurable Rules** – Define which formulae should be offloaded and where they should be stored.
- 🔄 **Automatic Operation** – Offloading happens automatically during install or upgrade operations.

## Usage
```
brew-offload add FORMULA
```
The specified FORMULA will be offloaded to a different directory. By default, the offload directory is `~/.offload`.

## Requirements
- Python 3.13 or later