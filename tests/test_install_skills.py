import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/install-skills.sh"


@pytest.mark.parametrize(
    "target,folders",
    [("codex", [".agents"]), ("claude", [".claude"]), ("both", [".agents", ".claude"])],
)
def test_install_selected_agents(tmp_path, target, folders):
    subprocess.run(["sh", str(SCRIPT), target], cwd=tmp_path, check=True)
    for folder in (".agents", ".claude"):
        installed = tmp_path / folder / "skills/constutil"
        assert installed.exists() == (folder in folders)
        if folder in folders:
            assert (installed / "SKILL.md").read_bytes() == (
                ROOT / "skills/constutil/SKILL.md"
            ).read_bytes()


def test_existing_install_requires_force(tmp_path):
    command = ["sh", str(SCRIPT), "both"]
    subprocess.run(command, cwd=tmp_path, check=True)
    skill = tmp_path / ".agents/skills/constutil/SKILL.md"
    skill.write_text("Personal edits")
    assert subprocess.run(command, cwd=tmp_path).returncode == 1
    assert skill.read_text() == "Personal edits"
    subprocess.run([*command, "--force"], cwd=tmp_path, check=True)
    assert skill.read_bytes() == (ROOT / "skills/constutil/SKILL.md").read_bytes()


def test_global_install(tmp_path):
    personal = tmp_path / "personal"
    subprocess.run(
        ["sh", str(SCRIPT), "both", "--global"],
        cwd=tmp_path,
        env={**os.environ, "HOME": str(personal)},
        check=True,
    )
    assert (personal / ".agents/skills/constutil/SKILL.md").is_file()
    assert (personal / ".claude/skills/constutil/SKILL.md").is_file()
    assert not (tmp_path / ".agents").exists()


def test_download_failure_does_not_install_partial_skill(tmp_path):
    script = tmp_path / "install-skills.sh"
    script.write_bytes(SCRIPT.read_bytes())
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    curl = bin_dir / "curl"
    curl.write_text("#!/bin/sh\nexit 22\n")
    curl.chmod(0o755)
    result = subprocess.run(
        ["sh", str(script), "both"],
        cwd=tmp_path,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
    )
    assert result.returncode != 0
    assert not (tmp_path / ".agents").exists()
    assert not (tmp_path / ".claude").exists()


def test_invalid_target_does_not_install(tmp_path):
    result = subprocess.run(["sh", str(SCRIPT), "unknown"], cwd=tmp_path)
    assert result.returncode == 2
    assert not (tmp_path / ".agents").exists()
