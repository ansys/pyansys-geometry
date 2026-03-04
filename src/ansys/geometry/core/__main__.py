# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""CLI for PyAnsys Geometry.

Usage:
    python -m ansys.geometry.core agent --env vscode --copy
    python -m ansys.geometry.core agent --env vscode --pointer
    python -m ansys.geometry.core agent --print
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

# Package metadata
PACKAGE_NAMESPACE = "ansys.geometry.core"
PACKAGE_NAME = "ansys-geometry-core"
PACKAGE_ECOSYSTEM = "pypi"


# =============================================================================
# Utility Methods
# =============================================================================


def find_workspace_root() -> Path | None:
    """Find workspace root by walking up from cwd."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            return parent
        if (parent / "pyproject.toml").exists():
            return parent
    return None


def get_package_dir() -> Path:
    """Get the package directory containing agent instructions."""
    return Path(__file__).parent


def get_instructions_path() -> Path:
    """Get path to agent instructions file."""
    return get_package_dir() / "AGENT.md"


def get_extended_docs_dir() -> Path:
    """Get path to extended agent documentation directory."""
    return get_package_dir() / "agent"


def get_instructions_content() -> str:
    """Read the agent instructions from installed package."""
    return get_instructions_path().read_text(encoding="utf-8")


def rewrite_links_for_copy(content: str, subdir_name: str) -> str:
    """Rewrite relative links in content to work from copied location."""
    import re

    pattern = r"\]\(agent/"
    replacement = f"]({subdir_name}/"
    return re.sub(pattern, replacement, content)


def format_for_cursor(content: str, source_path: Path) -> str:
    """Wrap content in Cursor rules MDC format."""
    return f"""---
description: PyAnsys Geometry usage instructions for AI assistants
globs: ["**/*.py"]
alwaysApply: false
---

<!-- Auto-generated from: {source_path} -->

{content}
"""


def ensure_gitignore(workspace: Path) -> None:
    """Add .agent/ to .gitignore."""
    gitignore = workspace / ".gitignore"
    marker = ".agent/"
    if gitignore.exists():
        content = gitignore.read_text()
        if marker not in content:
            with gitignore.open("a") as f:
                f.write(f"\n# Agent instructions (auto-generated)\n{marker}\n")
    else:
        gitignore.write_text(f"# Agent instructions (auto-generated)\n{marker}\n")


# =============================================================================
# Manifest Management
# =============================================================================


def load_manifest(agent_dir: Path) -> dict:
    """Load the manifest.json file, or return empty manifest."""
    manifest_file = agent_dir / "manifest.json"
    if manifest_file.exists():
        try:
            return json.loads(manifest_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"version": "1.0", "packages": []}


def save_manifest(agent_dir: Path, manifest: dict) -> None:
    """Save the manifest.json file."""
    manifest_file = agent_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def update_manifest_entry(
    manifest: dict,
    namespace: str,
    ecosystem: str,
    package_name: str,
    entry_file: str,
    extended_docs: list[str],
    mode: str,
    source_path: str,
) -> dict:
    """Add or update a package entry in the manifest."""
    # Find existing entry
    packages = manifest.get("packages", [])
    entry = None
    for pkg in packages:
        if pkg.get("namespace") == namespace:
            entry = pkg
            break

    if entry is None:
        entry = {"namespace": namespace}
        packages.append(entry)

    # Update entry
    entry["ecosystem"] = ecosystem
    entry["package_name"] = package_name
    entry["entry_file"] = entry_file
    entry["extended_docs"] = extended_docs
    entry["mode"] = mode
    entry["source"] = source_path
    entry["installed_at"] = datetime.now(timezone.utc).isoformat()

    manifest["packages"] = packages
    return manifest


def generate_readme(agent_dir: Path, manifest: dict) -> None:
    """Generate README.md from manifest."""
    packages = manifest.get("packages", [])

    lines = [
        "# Agent Instructions",
        "",
        "This directory contains agent instructions from installed packages.",
        "Agents can read these files for context about how to use the packages.",
        "",
        "## Installed Packages",
        "",
    ]

    if packages:
        lines.append("| Namespace | Ecosystem | Package | Entry File |")
        lines.append("|-----------|-----------|---------|------------|")
        for pkg in packages:
            namespace = pkg.get("namespace", "?")
            ecosystem = pkg.get("ecosystem", "?")
            package_name = pkg.get("package_name", "?")
            entry_file = pkg.get("entry_file", "?")
            lines.append(
                f"| `{namespace}` | {ecosystem} | {package_name} | "
                f"[{entry_file}]({entry_file}) |"
            )
        lines.append("")
    else:
        lines.append("*No packages installed yet.*")
        lines.append("")

    lines.extend(
        [
            "## Usage",
            "",
            "Each package provides its own installation command. For Python packages with",
            "agent instructions, you can typically run:",
            "",
            "```bash",
            "python -m <package> agent --copy",
            "```",
            "",
            "## Scanning Dependencies",
            "",
            "To install agent instructions from all packages in your requirements:",
            "",
            "```bash",
            "# Future: python -m agent_instructions scan requirements.txt",
            "# For now, run each package's agent command individually",
            "```",
            "",
            "---",
            "*Auto-generated manifest. Regenerate by running package agent commands.*",
            "",
        ]
    )

    readme_file = agent_dir / "README.md"
    readme_file.write_text("\n".join(lines), encoding="utf-8")


# =============================================================================
# File Copy Operations
# =============================================================================


def copy_all_instructions(workspace: Path, mode: str = "copy") -> tuple[Path, list[str]]:
    """Copy all agent instruction files to workspace with working links.

    Returns
    -------
    tuple[Path, list[str]]
        Main file path and list of extended doc relative paths.
    """
    agent_dir = workspace / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Main file with rewritten links
    main_content = get_instructions_content()
    main_content = rewrite_links_for_copy(main_content, PACKAGE_NAMESPACE)
    main_file = agent_dir / f"{PACKAGE_NAMESPACE}.md"
    main_file.write_text(main_content, encoding="utf-8")

    # Extended docs
    extended_dir = agent_dir / PACKAGE_NAMESPACE
    extended_dir.mkdir(parents=True, exist_ok=True)

    source_dir = get_extended_docs_dir()
    extended_docs = []

    if source_dir.exists():
        for src_file in source_dir.glob("*.md"):
            dst_file = extended_dir / src_file.name
            shutil.copy2(src_file, dst_file)
            extended_docs.append(f"{PACKAGE_NAMESPACE}/{src_file.name}")

    # Update manifest
    manifest = load_manifest(agent_dir)
    manifest = update_manifest_entry(
        manifest=manifest,
        namespace=PACKAGE_NAMESPACE,
        ecosystem=PACKAGE_ECOSYSTEM,
        package_name=PACKAGE_NAME,
        entry_file=f"{PACKAGE_NAMESPACE}.md",
        extended_docs=extended_docs,
        mode=mode,
        source_path=str(get_instructions_path()),
    )
    save_manifest(agent_dir, manifest)
    generate_readme(agent_dir, manifest)

    return main_file, extended_docs


def register_pointer_in_manifest(workspace: Path, mode: str = "pointer") -> None:
    """Register a pointer-mode entry in the manifest."""
    agent_dir = workspace / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    source_path = get_instructions_path()
    extended_dir = get_extended_docs_dir()
    extended_docs = []
    if extended_dir.exists():
        for doc in extended_dir.glob("*.md"):
            extended_docs.append(f"agent/{doc.name}")

    manifest = load_manifest(agent_dir)
    manifest = update_manifest_entry(
        manifest=manifest,
        namespace=PACKAGE_NAMESPACE,
        ecosystem=PACKAGE_ECOSYSTEM,
        package_name=PACKAGE_NAME,
        entry_file=str(source_path),
        extended_docs=extended_docs,
        mode=mode,
        source_path=str(source_path),
    )
    save_manifest(agent_dir, manifest)
    generate_readme(agent_dir, manifest)


# =============================================================================
# Pointer Block Management
# =============================================================================


def _make_pointer_block(
    pygeom_ref: str,
    regenerate_cmd: str,
    extended_docs: list[str] | None = None,
) -> tuple[str, str, str]:
    """Create a pointer block for single-file instruction tools."""
    start = "<!-- pygeom-agent-instructions:start -->"
    end = "<!-- pygeom-agent-instructions:end -->"

    extended_hint = ""
    if extended_docs:
        extended_hint = " (links to extended topics)"

    block = f"""{start}
## PyAnsys Geometry (ansys-geometry-core)

**IMPORTANT:** Before writing any code using `ansys.geometry.core`, you MUST:

1. **Read** the file `{pygeom_ref}` in this workspace
2. **Read linked files** as needed for your task{extended_hint}

Regenerate: `{regenerate_cmd}`
{end}"""

    return start, end, block


def _update_single_file_instructions(
    workspace: Path,
    pygeom_path: Path,
    target_file: Path,
    regenerate_cmd: str,
    default_header: str,
    extended_docs: list[str] | None = None,
) -> Path:
    """Append/refresh a pointer section in a single-file instructions file."""
    try:
        rel = pygeom_path.relative_to(workspace)
        pygeom_ref = str(rel).replace("\\", "/")
    except ValueError:
        pygeom_ref = str(pygeom_path).replace("\\", "/")

    start, end, block = _make_pointer_block(pygeom_ref, regenerate_cmd, extended_docs)

    if target_file.exists():
        text = target_file.read_text(encoding="utf-8", errors="replace")

        if start in text and end in text and text.index(start) < text.index(end):
            pre = text[: text.index(start)].rstrip()
            post = text[text.index(end) + len(end) :].lstrip()
            if pre:
                new_text = f"{pre}\n\n{block}\n"
            else:
                new_text = f"{block}\n"
            if post:
                new_text += f"\n{post}"
            new_text = new_text.rstrip() + "\n"
        else:
            new_text = text.rstrip() + "\n\n" + block + "\n"
    else:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        new_text = f"{default_header}\n\n{block}\n"

    target_file.write_text(new_text, encoding="utf-8")
    return target_file


def update_copilot_instructions(
    workspace: Path,
    pygeom_path: Path,
    mode: str,
    extended_docs: list[str] | None = None,
) -> Path:
    """Update .github/copilot-instructions.md with a pointer."""
    github_dir = workspace / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)
    copilot_file = github_dir / "copilot-instructions.md"

    return _update_single_file_instructions(
        workspace=workspace,
        pygeom_path=pygeom_path,
        target_file=copilot_file,
        regenerate_cmd=f"python -m ansys.geometry.core agent --env vscode --{mode}",
        default_header="# Copilot Instructions",
        extended_docs=extended_docs,
    )


def update_claude_instructions(
    workspace: Path,
    pygeom_path: Path,
    mode: str,
    extended_docs: list[str] | None = None,
) -> Path:
    """Update CLAUDE.md with a pointer."""
    claude_file = workspace / "CLAUDE.md"

    return _update_single_file_instructions(
        workspace=workspace,
        pygeom_path=pygeom_path,
        target_file=claude_file,
        regenerate_cmd=f"python -m ansys.geometry.core agent --env claude --{mode}",
        default_header="# Claude Code Instructions",
        extended_docs=extended_docs,
    )


# =============================================================================
# Command Handlers
# =============================================================================


def cmd_agent_copy(args: argparse.Namespace, workspace: Path) -> int:
    """Handle --copy mode: copy all files with working links."""
    env = args.env

    if env == "cursor":
        # Cursor: single self-contained MDC file
        content = get_instructions_content()
        formatted = format_for_cursor(content, get_instructions_path())
        cursor_dir = workspace / ".cursor" / "rules"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        output_path = cursor_dir / "pygeometry.mdc"
        output_path.write_text(formatted, encoding="utf-8")
        print(f"[OK] PyAnsys Geometry instructions written to: {output_path}")
        return 0

    # All other environments: copy to .agent/ with extended docs
    main_file, extended_docs = copy_all_instructions(workspace, mode="copy")
    ensure_gitignore(workspace)

    print(f"[OK] PyAnsys Geometry instructions copied to: {main_file}")
    if extended_docs:
        print(f"     Extended docs: {len(extended_docs)} files")
    print(f"     Manifest updated: {workspace / '.agent' / 'manifest.json'}")

    # For single-file tools, also add pointer
    if env in ("vscode", "copilot"):
        pointer_file = update_copilot_instructions(workspace, main_file, "copy")
        print(f"[OK] Added pointer to: {pointer_file}")
        print("     (Your existing instructions were preserved)")

    elif env == "claude":
        pointer_file = update_claude_instructions(workspace, main_file, "copy")
        print(f"[OK] Added pointer to: {pointer_file}")
        print("     (Your existing instructions were preserved)")

    return 0


def cmd_agent_pointer(args: argparse.Namespace, workspace: Path) -> int:
    """Handle --pointer mode: just add pointer to installed package."""
    env = args.env
    source_path = get_instructions_path()

    # Get extended doc paths relative to main file
    extended_dir = get_extended_docs_dir()
    extended_docs = []
    if extended_dir.exists():
        for doc in extended_dir.glob("*.md"):
            extended_docs.append(f"agent/{doc.name}")

    if env == "cursor":
        # Cursor doesn't support pointer mode well - use copy instead
        print("Note: Cursor works best with --copy mode. Using --copy.", file=sys.stderr)
        return cmd_agent_copy(args, workspace)
    
    # Register in manifest even for pointer mode
    register_pointer_in_manifest(workspace, mode="pointer")
    ensure_gitignore(workspace)

    if env in ("vscode", "copilot"):
        pointer_file = update_copilot_instructions(workspace, source_path, "pointer", extended_docs)
        print(f"[OK] Added pointer to installed package in: {pointer_file}")
        print(f"     Points to: {source_path}")
        print(f"     Manifest updated: {workspace / '.agent' / 'manifest.json'}")
        print("     (Your existing instructions were preserved)")

    elif env == "claude":
        pointer_file = update_claude_instructions(workspace, source_path, "pointer", extended_docs)
        print(f"[OK] Added pointer to installed package in: {pointer_file}")
        print(f"     Points to: {source_path}")
        print(f"     Manifest updated: {workspace / '.agent' / 'manifest.json'}")
        print("     (Your existing instructions were preserved)")

    elif env == "generic":
        print("PyDyna agent instructions are installed at:")
        print(f"  {source_path}")
        if extended_docs:
            print("\nExtended documentation:")
            for doc in extended_docs:
                print(f"  {source_path.parent / doc}")
        print(f"\nManifest updated: {workspace / '.agent' / 'manifest.json'}")

    return 0

def cmd_agent(args: argparse.Namespace) -> int:
    """Handle 'agent' subcommand."""
    content = get_instructions_content()

    # Print mode
    if args.print:
        try:
            print(content)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(content.encode("utf-8"))
        return 0
    
    # Find workspace
    if args.workspace:
        workspace = Path(args.workspace)
    else:
        workspace = find_workspace_root()
        if workspace is None:
            print("Error: Could not detect workspace root.", file=sys.stderr)
            print("Run from a git repo or specify --workspace PATH", file=sys.stderr)
            return 1
        
    # Determine mode
    if args.pointer:
        return cmd_agent_pointer(args, workspace)
    else:
        # Default to copy mode
        return cmd_agent_copy(args, workspace)
    

def main() -> int:
    """Execute the main CLI functionality."""
    parser = argparse.ArgumentParser(
        prog="python -m ansys.geometry.core",
        description="PyAnsys Geometry CLI utilities",
    )
    subparsers = parser.add_subparsers(dest="command")

    # agent subcommand
    agent_parser = subparsers.add_parser(
        "agent",
        help="Install agent instructions for AI assistants",
    )

    # Agent options
    agent_parser.add_argument(
        "--env",
        choices=["vscode", "cursor"],
        help="Target environment for agent instructions",
    )

    agent_parser.add_argument(
        "--print",
        action="store_true",
        help="Print instructions to console",
    )

    agent_parser.add_argument(
        "--workspace",
        type=str,
        help="Workspace directory (default: auto-detect if not specified)",
    )

    # Mode selection (mutually exclusive)
    mode_group = agent_parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--copy",
        action="store_true",
        help="Copy instructions to clipboard",
    )
    mode_group.add_argument(
        "--pointer",
        action="store_true",
        help="Show pointer to instructions",
    )

    args = parser.parse_args()

    if args.command == "agent":
        return cmd_agent(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())