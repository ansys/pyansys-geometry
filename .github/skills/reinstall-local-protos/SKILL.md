---
name: reinstall-local-protos
description: "Reinstalls the local ansys-api-discovery proto package synced to the current ApiServer branch. Use when: updating proto definitions from ApiServer, refreshing local gRPC stubs after proto changes, syncing ansys-api-discovery with an ApiServer feature branch, or re-running pip install after proto edits."
argument-hint: "Optionally specify the ApiServer base branch to diff against (default: origin/develop)"
---

# Reinstall Local Protos

## When to Use

Run this skill whenever you need the local `ansys-api-discovery` package to reflect proto changes made in the currently checked-out ApiServer branch. This is the standard workflow for testing PyAnsys Geometry against in-progress ApiServer changes before the proto package is officially published.

## Workspace Layout

| Folder | Purpose |
|--------|---------|
| `$env:APISERVER_ROOT\DomainModel\DomainModel.Protobuffer\ansys\api\discovery\` | Canonical proto sources (inside ApiServer) |
| `$env:PROTOS_DIR\ansys\api\discovery\` | Python proto package (destination for copy) |

## Procedure

### Step 1: Activate the virtual environment

Check the `PYANSYS_VENV` environment variable first:
```powershell
$env:PYANSYS_VENV
```
If it is set, activate it:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& "$env:PYANSYS_VENV\Scripts\Activate.ps1"
```
If `PYANSYS_VENV` is not set, look for a `.venv` directory in the pyansys-geometry workspace folder (or its parent) and activate from there.

### Step 2: Clean and reset ansys-api-discovery

Change to the `ansys-api-discovery` workspace folder and remove all untracked and generated files:
```powershell
Set-Location $env:PROTOS_DIR
git clean -fdx
```

### Step 3: Pull latest main

Pull the latest `main` branch to start from a clean, up-to-date baseline:
```powershell
git pull origin main
```

### Step 4: Copy proto changes from the ApiServer branch

Determine which `.proto` files under `ansys/api/discovery/` have been modified or added in the current ApiServer branch compared to its base branch (default: `origin/develop`):
```powershell
$apiServerRoot = $env:APISERVER_ROOT
$protoSrcBase  = "$apiServerRoot\DomainModel\DomainModel.Protobuffer"
$protoDstBase  = $env:PROTOS_DIR
$baseBranch    = "origin/develop"   # adjust if the argument specifies a different base

$changedProtos = git -C $apiServerRoot diff --name-only HEAD $baseBranch `
    -- "DomainModel/DomainModel.Protobuffer/ansys/api/discovery/"

foreach ($rel in $changedProtos) {
    $src = Join-Path $apiServerRoot $rel.Replace("/", "\")
    # Map DomainModel/DomainModel.Protobuffer/<rest> -> $protoDstBase\<rest>
    $suffix = $rel.Replace("DomainModel/DomainModel.Protobuffer/", "").Replace("/", "\")
    $dst = Join-Path $protoDstBase $suffix
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
    Copy-Item $src $dst -Force
    Write-Host "Copied: $rel"
}
```

If no files are listed, the current ApiServer branch has no proto changes relative to `origin/develop` and no copy is needed.

> **Note:** Only `.proto` source files are copied. The generated `_pb2.py` / `_pb2.pyi` / `_pb2_grpc.py` / `_pb2_grpc.pyi` files are regenerated automatically by `pip install .` in Step 5.

### Step 5: Install the updated package

Run `pip install .` from the `ansys-api-discovery` folder. This regenerates all protobuf stubs from the updated `.proto` files and installs the package into the active virtual environment:
```powershell
Set-Location $env:PROTOS_DIR
pip install .
```

Confirm the install succeeded and verify the version shown matches expectations.

## Completion Criteria

- `git clean -fdx` completed without errors in `ansys-api-discovery`.
- `git pull origin main` succeeded.
- All changed `.proto` files from the ApiServer branch are present in `$env:PROTOS_DIR\ansys\api\discovery\`.
- `pip install .` completed without errors.
- The active Python environment now imports the updated proto stubs.

## Troubleshooting

| Issue | Action |
|-------|--------|
| `git clean -fdx` removes files you want to keep | Stash your changes first: `git stash` before running this skill |
| `pip install .` fails on proto compilation | Ensure `grpcio-tools` is installed in the venv: `pip install grpcio-tools` |
| Changed proto list is empty but you expect changes | Check that `$baseBranch` is correct; try `origin/main` if the ApiServer default branch differs |
| Import errors after install | Restart any running Python session to pick up the new stubs |
