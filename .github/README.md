# Lunar OS GitHub Actions

This repository uses GitHub Actions to automatically build the Lunar OS ISO.

## Workflow

The `.github/workflows/build-iso.yml` workflow:

- **Triggers**: Push to main/master, pull requests, or manual workflow dispatch
- **Runtime**: Ubuntu with live-build tools
- **Timeout**: 6 hours (builds can take 45-90 minutes)
- **Output**: ISO file and SHA256 checksum uploaded as artifacts

## Manual Build

To trigger a manual build:

1. Go to the "Actions" tab in GitHub
2. Select "Build Lunar OS ISO"
3. Click "Run workflow"
4. Optionally enable "Create a GitHub Release with the ISO"
5. Click "Run workflow"

## Artifacts

After a successful build:

- **lunar-os-iso**: The ISO file (retained for 7 days)
- **lunar-os-checksum**: SHA256 checksum (retained for 7 days)

## Releases

If you enable "Create a GitHub Release" when triggering the workflow, it will:

- Create a new release with a version timestamp
- Upload the ISO file
- Upload the checksum
- Include build notes

## Local Build

If you prefer to build locally, see [docs/BUILDING.md](../docs/BUILDING.md).
