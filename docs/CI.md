# Continuous Integration

[GitHub Actions](http://github.com/features/actions) [Workflows](https://github.com/Artheau/SpriteSomething/tree/master/.github/workflows)

1. [Continuous Integration](https://github.com/Artheau/SpriteSomething/blob/master/.github/workflows/ci.yml)
   1. Install & Test (Ubuntu-latest, Ubuntu-16.04, MacOS, Windows; 3.7)
      - Run on OS (Ubuntu-latest, Ubuntu-16.04, MacOS, Windows)
      - Run on python 3.7
      - Checkout Commit
      - Install python
      - Install Dependencies via pip
      - Start Virtual Display driver
      - Run unittest
   1. Install & Build (Ubuntu-latest, Ubuntu-16.04, MacOS, Windows; 3.7)
      - Same as Install from Install & Test
      - Build Binary using pyinstaller
      - Prepare Binary Artifact for upload
      - Upload Binary Artifact
   1. Install & Prepare Release (Ubuntu-latest, Ubuntu-16.04, MacOS, Windows; 3.7)
      - Same as Install from Install & Test
      - Download Binary
      - Prepare AppVersion & Release
      - Upload AppVersion
      - Upload Archive
   1. Deploy GHReleases (Ubuntu-latest, 3.7)
      - Download AppVersion
      - Download Ubuntu Archive
      - Download MacOS Archive
      - Download Windows Archive
      - Print Debug Info
      - Read RELEASENOTES.md
      - Create a Release (if master)
      - Upload Ubuntu Asset (if master)
      - Upload MacOS Asset (if master)
      - Upload Windows Asset (if master)
      - Send Discord notification
   1. Prepare GHPages (Ubuntu-latest)
      - Download AppVersion
      - Prepare Pages
      - Upload Pages Artifact
   1. Deploy Pages (Ubuntu-latest)
      - Download Pages
      - Post to Pages (inactive)
1. [Pushes to master](https://github.com/Artheau/SpriteSomething/blob/master/.github/workflows/on-release.yml)
   1. CI Step#iv, if Release created (MacOS, 3.7)
      - Send Discord notification

- [CI scripts](https://github.com/Artheau/SpriteSomething/tree/master/resources/ci/common)
- [Build script](https://github.com/Artheau/SpriteSomething/blob/master/source/meta/build.py)
- [Spec file for pyinstaller](https://github.com/Artheau/SpriteSomething/blob/master/source/SpriteSomething.spec)
- [Entrypoint script](https://github.com/Artheau/SpriteSomething/blob/master/SpriteSomething.py)
