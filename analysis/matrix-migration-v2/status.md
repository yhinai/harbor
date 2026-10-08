# Matrix migration v2: runtime operational

**Verified, 2026-10-08:** The project runs at `matrix:/Users/matrix/projects/harbor`. The v1 Homebrew permission blocker is resolved by a private user-prefix installation using official binaries. No sudo, ownership changes, shared Homebrew changes, credentials transfer, or paid model calls were needed.

**Verified:** Lima 2.2.1, Colima 0.10.3, uv 0.12.23, Docker CLI 29.8.2, Compose 5.6.0, and Buildx 0.38.0 are installed under `/Users/matrix/.local/harbor-runtime`. GitHub release digests were checked for the Lima, Colima, uv, Compose, and Buildx downloads. The Docker archive's locally computed hash is recorded without claiming a separate published digest check. Installation URLs and hashes accompany this record. Python 3.12.15 and Harbor 0.24.0 are installed in the ignored remote virtual environment.

**Verified:** The dedicated `frontier-portfolio` VM is running with 10 CPUs and 10 GiB memory on the 12-core/16-GiB host. It has a 60-GiB data disk and uses macOS virtualization. The Docker daemon reports version 29.5.2; this differs from the host CLI version. Default Docker context activation was disabled. The VM survives the SSH command ending; automatic startup after reboot was not configured or tested.

**Verified:** New harness v1.3.0 passed actual Harbor integration and all five canonical Harbor oracles on matrix. Mock stream tests, budget checks, synthetic output-exhaustion classification, and an explicit Docker cancellation check passed. Frozen artifact checks passed before and after validation. See [harness findings](../harness-v1.3.0/findings.md) and [validation evidence](../harness-v1.3.0/evidence/validation-summary.json).

The runtime VM remains running. Completed test containers were cleaned up; no paid agent or evaluation job is running. The local checkout is retained as a synchronization copy, not deleted. New work remains separate from the frozen Day 1 artifacts.

For reproducible setup, run `provision.py` then `finish-provision.sh` on matrix from the project directory. These download/install tools; they do not invoke a model. For normal use, source `tools/harness-v1.3.0/matrix-env.sh` on matrix. Dependency versions are saved in the harness evidence. Do not copy local caches or credentials to the remote machine.
