"""Build the GitHub Pages site from the package README."""

from pathlib import Path
from shutil import copytree, make_archive

import markdown

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    content = markdown.markdown(readme, extensions=["fenced_code", "tables", "toc"])
    destination = ROOT / "site"
    destination.mkdir(exist_ok=True)
    (destination / ".nojekyll").touch()
    (destination / "index.md").write_text(readme, encoding="utf-8")
    copytree(
        ROOT / "skills" / "constutil", destination / "skills" / "constutil", dirs_exist_ok=True
    )
    make_archive(
        str(destination / "skills" / "constutil"),
        "zip",
        root_dir=destination / "skills",
        base_dir="constutil",
    )
    copytree(
        ROOT / "examples",
        destination / "examples",
        dirs_exist_ok=True,
        ignore=lambda directory, names: [name for name in names if name == "__pycache__"],
    )
    skill = (ROOT / "skills" / "constutil" / "SKILL.md").read_text(encoding="utf-8")
    (destination / "llms-full.txt").write_text(
        readme + "\n\n---\n\n# Shared constutil coding skill\n\n" + skill, encoding="utf-8"
    )
    (destination / "llms.txt").write_text(
        """# constutil

> Typed constant definitions and groups for Python 3.10+, with no runtime dependencies.

ConstDef stores a scalar value and display name; ConstGroup provides ordered
lookup and enumeration. Comparisons use Python equality without coercion or case
folding. Derive groups directly from generic specializations; do not extend
populated groups. The optional skill recommends a constants package layout.

## Documentation

- [README and API](https://constutil.patchfork.dev/index.md):
  examples, behavior, compatibility, and setup.
- [Full context](https://constutil.patchfork.dev/llms-full.txt):
  README and skill instructions together.

## Skills

- [constutil skill](https://constutil.patchfork.dev/skills/constutil/SKILL.md):
  shared Codex and Claude Code conventions, lookup, and existence checks.
- [Codex metadata](https://constutil.patchfork.dev/skills/constutil/agents/openai.yaml):
  optional skill discovery metadata.

## Examples

- [Running examples](https://constutil.patchfork.dev/examples/README.md):
  uv commands and expected behavior.
- [Days](https://constutil.patchfork.dev/examples/days.py): integer choices and validation.
- [Saturn moons](https://constutil.patchfork.dev/examples/saturn_moons.py):
  string choices and typed metadata.
""",
        encoding="utf-8",
    )
    (destination / "index.html").write_text(
        """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Typed constant definitions and groups for Python.">
<link rel="canonical" href="https://constutil.patchfork.dev/">
<link rel="alternate" type="text/markdown" href="index.md">
<link rel="describedby" href="llms.txt">
<title>constutil — Typed constants for Python</title>
<style>
:root { color-scheme: light dark; font-family: system-ui, sans-serif; line-height: 1.65; }
body { max-width: 900px; margin: auto; padding: 2rem 1.2rem 5rem; }
h1 { font-size: 3rem; letter-spacing: -.05em; margin-bottom: .3rem; }
h2 { margin-top: 2.5rem; border-bottom: 1px solid #8886; padding-bottom: .3rem; }
a { color: light-dark(#145cb3, #8ac2ff); text-underline-offset: .15em; }
pre { padding: 1.2rem; overflow-x: auto; border: 1px solid #8885; border-radius: .6rem; }
code { font-family: ui-monospace, monospace; font-size: .9em; }
pre, :not(pre) > code { background: light-dark(#f2f5f8, #1d2530); }
:not(pre) > code { padding: .12rem .25rem; border-radius: .2rem; }
table { display: block; overflow-x: auto; border-collapse: collapse; }
th, td { text-align: left; padding: .6rem .8rem; border: 1px solid #8885; }
</style></head><body><main>
"""
        + content
        + "\n</main></body></html>\n"
    )


if __name__ == "__main__":
    main()
