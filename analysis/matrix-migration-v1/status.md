# Matrix migration v1

Recorded 2026-10-08. No paid calls or task revisions.

**Verified:** SSH alias `matrix` reaches an Apple Silicon macOS host as user `matrix`. It reports 12 logical CPU cores, 16 GiB RAM, virtualization support, and approximately 168 GiB free disk. GitHub HTTPS read access works.

**Verified:** Cloned `https://github.com/yhinai/harbor.git`, branch `main`, into `/Users/matrix/projects/harbor`, initially at `32cf32f658358352bcae09c4a35c86f08122053b`. The clone contains the research, decisions, task packages, validation evidence, findings, deliverables, and frozen archive tracked in Git. No credentials, local environment files, build caches, virtual environments, or temporary trial directories were copied. Raw frozen trajectories remain in the submission ZIP as designed.

**Verified on matrix:** All 457 archive artifact hashes match the frozen manifest. All 344 manifest artifacts present as loose files also match. The archive SHA256 is `efdf99bd59590cb22cf45268f1caa9ea6df7b2df71345fdfac83a2e3d7611c7f`.

**Blocked:** Docker, Colima, uv, and the required Python runtime are absent; system Python is 3.9.6. Attempting `HOMEBREW_NO_AUTO_UPDATE=1 /opt/homebrew/bin/brew install colima docker uv` failed because user `matrix` cannot write required Homebrew directories. Homebrew belongs to another account. No ownership or permissions were changed, no unrelated tap was trusted, and no alternative installation workaround was attempted.

**Next prerequisite:** An administrator or the existing Homebrew owner must install `colima`, `docker`, and `uv` for this host, with binaries usable by `matrix`. Then resume provisioning a dedicated Docker profile and isolated Python environment, and perform the offline Harbor integration checks. Repository transfer is complete; runtime migration and harness validation are not complete. No job is running on matrix and no paid runner has been enabled.

The local checkout remains a preserved source and synchronization copy. Do not delete it or transfer its credentials. Before remote edits, pull `main` with fast-forward only and check for active writers. Commit and push subsequent milestones, then fast-forward the other checkout. Frozen artifacts remain immutable; any harness revision goes outside the frozen tree under a new version.
