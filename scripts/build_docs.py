"""Build the GitHub Pages site from the package README."""

from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    content = markdown.markdown(
        (ROOT / "README.md").read_text(), extensions=["fenced_code", "tables", "toc"]
    )
    destination = ROOT / "site"
    destination.mkdir(exist_ok=True)
    (destination / ".nojekyll").touch()
    (destination / "index.html").write_text(
        """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Typed constant definitions and groups for Python.">
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
