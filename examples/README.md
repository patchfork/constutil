# Runnable examples

Install [uv](https://docs.astral.sh/uv/) and clone this repository. From its root:

```sh
uv run examples/days.py
uv run examples/days.py 6
uv run examples/saturn_moons.py
uv run examples/saturn_moons.py rhea
```

`uv run` prepares the environment and installs the local `constutil` package;
no PyPI release is needed. From inside `examples/`, use
`uv run --project .. days.py 6` or `uv run --project .. saturn_moons.py rhea`.

The day example uses integer constants, a default, member access, enumeration,
and membership checks. The moon example adds typed metadata to string constants.

Invalid input demonstrates explicit missing-value handling and exits with code 2:

```sh
uv run examples/days.py 8
uv run examples/saturn_moons.py TITAN
```

`TITAN` does not match the stored value `titan`; comparisons are case-sensitive.
These examples define groups in one file for easy execution. In an application,
put the group definitions in a `constants` package, as described by the reusable
[skill](https://github.com/patchfork/constutil/tree/main/skills/constutil).
