# constutil

Typed constant definitions and groups for Python, with no runtime dependencies.

`ConstDef` stores a value and a display name. `ConstGroup` collects named definitions
and provides ordered enumeration, lookup, and validation. They can describe simple
choices or richer records without requiring Python's `enum.Enum`.

## Installation

Requires **Python 3.10 or newer**.

```sh
pip install constutil
```

Until the first PyPI release, install directly from GitHub:

```sh
pip install git+https://github.com/patchfork/constutil.git
```

## Days of the week

```python
from constutil import IntConstDef, IntConstGroup


class Day(IntConstGroup):
    MONDAY = IntConstDef(1, "Monday")
    TUESDAY = IntConstDef(2, "Tuesday")
    WEDNESDAY = IntConstDef(3, "Wednesday")
    THURSDAY = IntConstDef(4, "Thursday")
    FRIDAY = IntConstDef(5, "Friday")
    SATURDAY = IntConstDef(6, "Saturday")
    SUNDAY = IntConstDef(7, "Sunday")

    _default_constant = MONDAY


assert Day.MONDAY.value == 1
assert Day.MONDAY.name == "Monday"
assert Day.get_default() is Day.MONDAY
assert Day.get_by_value(1) is Day.MONDAY
assert Day.get_constant(name="Monday") is Day.MONDAY
assert Day.get_by_constant_name("MONDAY") is Day.MONDAY
assert Day.get_all_values() == (1, 2, 3, 4, 5, 6, 7)
assert Day.get_as_pairs()[0] == (1, "Monday")
assert Day.get_by_value("1") is None
assert Day.get_by_name("monday") is None
```

The attribute name (`MONDAY`), display name (`Monday`), and stored value (`1`)
are distinct. `.name` means display text, not the Python attribute name.

## Moons of Saturn: additional metadata

```python
from dataclasses import dataclass
from constutil import ConstDef, ConstGroup


@dataclass(frozen=True, slots=True)
class MoonDef(ConstDef[str]):
    discovered_by: str
    discovery_year: int


class SaturnMoon(ConstGroup[MoonDef]):
    TITAN = MoonDef("titan", "Titan", "Christiaan Huygens", 1655)
    IAPETUS = MoonDef("iapetus", "Iapetus", "Giovanni Domenico Cassini", 1671)
    RHEA = MoonDef("rhea", "Rhea", "Giovanni Domenico Cassini", 1672)


moon = SaturnMoon.get_by_value("titan")
assert moon is not None
assert moon.discovery_year == 1655  # The result retains the MoonDef type.
assert SaturnMoon.get_all_constant_names() == ("TITAN", "IAPETUS", "RHEA")
assert SaturnMoon.get_name("TITAN") is None
```

## String constants and custom records

`IntConstDef` and `StrConstDef` are aliases for `ConstDef[int]` and `ConstDef[str]`.
`IntConstGroup` and `StrConstGroup` are aliases for their corresponding specialized
groups. The aliases do not introduce new runtime classes.

```python
from constutil import StrConstDef, StrConstGroup


class Season(StrConstGroup):
    SPRING = StrConstDef("spring", "Spring")
    SUMMER = StrConstDef("summer", "Summer")
    AUTUMN = StrConstDef("autumn", "Autumn")
    WINTER = StrConstDef("winter", "Winter")


assert Season.get_value("Spring") == "spring"
assert Season.is_valid_value("SPRING") is False
```

A custom member class does not have to inherit `ConstDef`. It must expose a
`.value` of type `int | str` and a `.name` of type `str`, as expressed by the
exported `ConstantMember` protocol. Pass the concrete member class to
`ConstGroup[YourMember]`; the protocol is a static typing contract, not a runtime
member-discovery type. Mutable dataclasses may also implement that contract.

## Runnable examples

Clone the repository and run from its root:

```sh
uv run examples/days.py 6
uv run examples/saturn_moons.py rhea
```

`uv` installs this checkout automatically; no published release is needed. See
[examples/README.md](https://github.com/patchfork/constutil/tree/main/examples)
for default runs and invalid-input demonstrations.

## Behavior

### Comparison and lookup

All value, display-name, and attribute-name comparisons use **ordinary Python
`==`**, with no string conversion, whitespace trimming, or case normalization.
`1` does not match `"1"`, and `"titan"` does not match `"TITAN"`. Python's own
numeric equality still applies: `1 == True == 1.0`. Exact comparison does not
mean strict type identity.

`get_constant(value=None, name=None)` retains a combined lookup interface:

- A positional argument is a value: `Day.get_constant(1)`.
- Use `name="Monday"` to search by display name.
- A non-`None` value takes precedence when both arguments are supplied.
- No value and no name raises `ValueError`; a missing match returns `None`.
- All single-result lookups return the first match in declaration order.

### Enumeration, membership, and inheritance

Public attributes matching the declared member type are discovered in declaration
order. For a parameterized member such as `ConstDef[int]`, discovery also checks
its value with `isinstance(value, int)`. Unrelated attributes and wrong value types
are skipped. Prefix auxiliary attributes with `_` to exclude them explicitly.

**Inheritance is not meant to be derived beyond the generic derivations**:
use `class Day(ConstGroup[IntConstDef])`, its `IntConstGroup` alias, or a custom
record derived from `ConstDef[str]` as above. Do not extend a populated group or
build extra generic inheritance hierarchies. Enumeration inspects only the
concrete group's own class dictionary: inherited attributes may be accessible
through Python but are not included in that child's enumeration or lookup.

Members can be freely constructed. There is no singleton or uniqueness guarantee;
duplicate values, duplicate names, and multiple attributes referencing the same
member are allowed. `is_valid()` uses member equality, not identity. With
`ConstDef`, dataclass equality compares value and name and requires the same
runtime definition class.

`ConstDef` is a frozen dataclass. Groups are ordinary Python classes:
their attributes can be reassigned, and enumeration reflects changes immediately.
Each enumeration returns a fresh tuple or dictionary. A configured default is
returned as-is and is not required to belong to the group; absent defaults are
`None`. Custom mutable records remain mutable.

### API reference

| Method | Result |
| --- | --- |
| `get_default()` | Configured member or `None` |
| `get_all()` | Tuple of members |
| `get_all_map()` | Fresh attribute-name → member dictionary |
| `get_all_values()` | Tuple of stored values |
| `get_all_names()` | Tuple of display names |
| `get_all_constant_names()` | Tuple of Python attribute names |
| `get_as_pairs()` | Tuple of `(value, display_name)` pairs; value types preserved |
| `get_constant(value=None, name=None)` | Matching member or `None` |
| `get_by_value(value)` | Member matching the stored value or `None` |
| `get_by_name(name)` | Member matching the display name or `None` |
| `get_by_constant_name(name)` | Member matching the attribute name or `None` |
| `get_name(value)` | Display name or `None` |
| `get_value(name)` | Stored value or `None` |
| `is_valid(member)` | Whether an equal member exists in the group |
| `is_valid_value(value)` | Whether a member has an equal stored value |
| `is_value(member, value)` | Whether the supplied member's value equals `value` |
| `get_filtered(members)` | List copy of the input; **does not filter or validate membership** |
| `get_filtered_as_pairs(members)` | List of `(str(value), display_name)` pairs from the input |
| `has_required(values)` | **Exact set equality** with all group values |

The last three helpers intentionally retain their original behavior. Filter helpers
preserve input order and duplicates and accept foreign members. `has_required()`
ignores order and duplicates, but rejects missing or extra values. `is_value()`
does not check membership. Pair serialization in `get_filtered_as_pairs()` is an
output conversion, not a lookup comparison.

Lookup results preserve the declared member type. Value-only convenience methods
return `int | str` (and `None` for a missing lookup); use the typed member's `.value`
when the narrower scalar type matters. Annotations do not validate constructor
arguments at runtime.

## Python compatibility

The minimum is **Python 3.10**, determined by the features actually used:

| Feature | Introduced |
| --- | --- |
| `typing.Generic`, `TypeVar` | Python 3.5 |
| Dataclasses | Python 3.7 |
| `typing.Protocol`, `get_args`, `get_origin` | Python 3.8 |
| Built-in collection annotations such as `tuple[str, ...]` | Python 3.9 |
| Union annotations such as `MemberT | None` | Python 3.10 |
| `@dataclass(slots=True)` in optional metadata subclasses | Python 3.10 |

The generic base deliberately omits `slots=True`: older Python versions raise a
`TypeError` when instantiating a frozen, slotted generic alias because `typing`
tries to assign `__orig_class__`. Frozen definitions without slots work across the
supported versions. A subclass may use slots, but still inherits the base instance
dictionary.

Generic discovery uses `__orig_bases__`; it does not need Python 3.12's
`types.get_original_bases` or PEP 695 type-parameter syntax. The package includes
`py.typed`. CI tests Python 3.10–3.14. See the official
[dataclass documentation](https://docs.python.org/3.10/library/dataclasses.html),
[typing documentation](https://docs.python.org/3.10/library/typing.html), and
[Python 3.10 changes](https://docs.python.org/3.10/whatsnew/3.10.html).

## Adopt the coding skill (Codex and Claude Code)

The repository includes an opinionated, reusable
[constutil skill](https://github.com/patchfork/constutil/tree/main/skills/constutil).
It directs an agent to use `constutil` for related constant values, usually in a
`constants/` package, and explains naming, access, lookup, and existence checks.
Installing the Python dependency alone does **not** install the skill.

For one project, copy the complete `skills/constutil/` directory from this
repository to `<your-project>/.agents/skills/constutil/` and commit it. From that
project's root, with this repository cloned alongside it:

```sh
mkdir -p .agents/skills
cp -R ../constutil/skills/constutil .agents/skills/constutil
```

For personal use across projects, copy the directory to
`~/.agents/skills/constutil/` instead. Other agents supporting `SKILL.md` can use
the same skill folder in their own skill-discovery location. In Codex, invoke it
as `$constutil`, or let Codex select it for matching tasks. See the official
[skill installation and discovery documentation](https://learn.chatgpt.com/docs/build-skills).

To make this an always-applicable project convention, also add this instruction
to the consuming project's `AGENTS.md` (skill selection alone is task-dependent):

```text
Always use constutil when grouping related Python constant values. Keep groups
in the relevant constants package unless the existing package structure calls
for another location. Follow .agents/skills/constutil/SKILL.md for definition
and member names, access, exact lookup, and existence checks.
```

### Download from the documentation site

The site serves the same maintained skill files as this repository:

- [Skill instructions](https://constutil.patchfork.dev/skills/constutil/SKILL.md)
- [Codex metadata](https://constutil.patchfork.dev/skills/constutil/agents/openai.yaml)
- [Complete skill ZIP](https://constutil.patchfork.dev/skills/constutil.zip)

Extract the ZIP into `.agents/skills/` for Codex or `.claude/skills/` for Claude
Code. It contains a `constutil/` directory. Review the instructions and commit the
installed skill into your project. Installing the Python package does not install
or activate the skill automatically.

### Claude Code

Use the **same** `skills/constutil/` folder; the `SKILL.md` instructions are shared.
From the consuming project's root:

```sh
mkdir -p .claude/skills
cp -R ../constutil/skills/constutil .claude/skills/constutil
```

Commit that folder for your team. For personal use across projects, copy it to
`~/.claude/skills/constutil/`. Invoke it as `/constutil`, or let Claude select it
when the task matches. The optional `agents/openai.yaml` file supplies Codex UI
metadata; Claude uses `SKILL.md`.

Add the same always-use instruction shown above to `CLAUDE.md`, changing the
reference to `.claude/skills/constutil/SKILL.md`. This makes the project convention
available each session while the skill supplies the detailed usage guidance.
See [Claude Code's skill documentation](https://code.claude.com/docs/en/skills).

The skill has no dependency on a framework or another skill. Keep its version
aligned with the library version when updating it.

## Documentation for agents

- [llms.txt](https://constutil.patchfork.dev/llms.txt): concise index of documentation,
  examples, and skill instructions.
- [index.md](https://constutil.patchfork.dev/index.md): this README as plain Markdown.
- [llms-full.txt](https://constutil.patchfork.dev/llms-full.txt): the README and shared
  skill instructions in one text file.

These files and the downloadable skill are generated from the repository on every
Pages deployment. `llms.txt` is a discovery aid; it does not install skills or make
an agent follow them automatically.

## Development

```sh
uv sync --locked
uv run pytest --cov=constutil --cov-report=term-missing
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv build
uv run twine check dist/*
uv run python scripts/build_docs.py
```

Tests execute the Python examples in this README as well as checking discovery,
comparison, defaults, metadata, aliases, and helper semantics. Documentation is
generated directly from this file into `site/index.html`, so the package README
and website share one source.

## Publishing

### PyPI

The `pypi_publish.yml` workflow runs on a published GitHub release, tests the package
on Python 3.10–3.14, checks types and formatting, verifies that the release tag
matches the package version, builds a wheel and source distribution, checks their
metadata, and publishes via PyPI Trusted Publishing. It does not require an API token.

One-time setup:

1. Create a GitHub environment named `pypi` in `patchfork/constutil`.
2. On PyPI, configure a pending publisher for `constutil` (or a trusted publisher
   if you already own the project): owner `patchfork`, repository `constutil`,
   workflow filename `pypi_publish.yml`, environment `pypi`.
3. Update `project.version` in `pyproject.toml`, run `uv lock`, and commit the changes.
4. Publish a GitHub release with a matching tag, for example `v1.0.0`.

PyPI project-name availability is decided by PyPI when registering or publishing.
See [PyPI's Trusted Publishing guide](https://docs.pypi.org/trusted-publishers/).

### GitHub Pages

Select **GitHub Actions** under the repository's **Settings → Pages → Build and
deployment → Source**. The `pages.yml` workflow builds this README and deploys it
on pushes to `main`, or through a manual workflow run.

The published site is [constutil.patchfork.dev](https://constutil.patchfork.dev/).
Its DNS record is `CNAME constutil → patchfork.github.io` (without a repository
path). The repository's Pages custom-domain setting must also be
`constutil.patchfork.dev`; this Actions deployment does not use a `CNAME` file.
HTTPS is managed by GitHub Pages.

See [GitHub's Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## License

MIT. See [LICENSE](https://github.com/patchfork/constutil/blob/main/LICENSE).
