"""Machine-path resolution for the builder scripts.

These helpers are the ONLY sanctioned way to resolve machine paths in
this repo. There are deliberately NO defaults: a location that exists
on only one machine must be supplied explicitly through the
environment, so a script can never silently read from or write to
another machine's disk.

Required environment variables:
  BRICKHOUSE_WORKDIR -- the lyric-type working directory: the folder
      holding the .ecproj projects the builder reads and writes.
  EFFECTCRAFT_CLI -- the path of the effectcraft-cli binary that
      builder/ec_driver.py drives.
"""
import os
from pathlib import Path


def workdir() -> Path:
    """Return BRICKHOUSE_WORKDIR as a Path.

    Raises RuntimeError naming the variable when it is unset or empty.
    """
    value = os.environ.get("BRICKHOUSE_WORKDIR")
    if not value:
        raise RuntimeError(
            "BRICKHOUSE_WORKDIR is not set: export BRICKHOUSE_WORKDIR="
            "<path to the lyric-type working directory (the folder "
            "holding the .ecproj projects)> before running the builder "
            "scripts; there is no default."
        )
    return Path(value)


def ec_cli() -> str:
    """Return EFFECTCRAFT_CLI (the effectcraft-cli binary path).

    Raises RuntimeError naming the variable when it is unset or empty.
    """
    value = os.environ.get("EFFECTCRAFT_CLI")
    if not value:
        raise RuntimeError(
            "EFFECTCRAFT_CLI is not set: export EFFECTCRAFT_CLI="
            "<path to the effectcraft-cli binary> before running "
            "builder/ec_driver.py; there is no default."
        )
    return value
