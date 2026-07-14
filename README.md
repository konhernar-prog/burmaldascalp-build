# zovscalpick-build (private)

Build inputs + CI for producing ZoVscalpick binaries. **Private** — not for distribution.

- `rebuild/ZoVscalpick.spec` — Windows build (PyInstaller).
- `rebuild/ZoVscalpick-mac.spec` — macOS build (.app). Runs only on macOS.
- `.github/workflows/build-macos.yml` — builds `ZoVscalpick.app` on a GitHub macОS runner
  and uploads it as an artifact. Trigger via **Actions → build-macos → Run workflow**.
