"""Run from the repository root: uv run examples/saturn_moons.py [moon-value]."""

import argparse

from constutil import ConstDef, ConstGroup


class MoonDef(ConstDef[str]):
    discovered_by: str
    discovery_year: int


class SaturnMoon(ConstGroup[MoonDef]):
    TITAN = MoonDef("titan", "Titan", "Christiaan Huygens", 1655)
    IAPETUS = MoonDef("iapetus", "Iapetus", "Giovanni Domenico Cassini", 1671)
    RHEA = MoonDef("rhea", "Rhea", "Giovanni Domenico Cassini", 1672)


def main() -> None:
    parser = argparse.ArgumentParser(description="Look up a moon using an exact string value.")
    parser.add_argument("moon", nargs="?", default="titan")
    args = parser.parse_args()
    moon = SaturnMoon.get_by_value(args.moon)
    if moon is None:
        parser.error(f"Unknown moon {args.moon!r}; choose one of {SaturnMoon.get_all_values()}")
    print(f"{moon.name}: discovered in {moon.discovery_year} by {moon.discovered_by}")
    print(f"Attribute names: {SaturnMoon.get_all_constant_names()}")
    print(f"Display names: {SaturnMoon.get_all_names()}")
    print(f"Uppercase value 'TITAN' exists: {SaturnMoon.is_valid_value('TITAN')}")


if __name__ == "__main__":
    main()
