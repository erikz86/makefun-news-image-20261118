"""Entrypoint: render the 18 November 2026 front page to entry.png.

The grader runs this program with no network and a writable output
directory named by MAKEFUN_OUTPUT_DIR (default: the current directory).
All drawing lives in generate_image.py; this module only decides where
the finished PNG goes and reports what it wrote.
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generate_image

MAX_BYTES = 1048576   # the competition gate: at most 1 MiB
MAX_SIDE = 1024       # ... and at most 1024 by 1024 pixels


def output_path():
    """Where the finished image goes: $MAKEFUN_OUTPUT_DIR/entry.png,
    or ./entry.png when the variable is unset."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "entry.png")


def check_entry(path, size):
    """Read the finished file back and confirm it passes the gate's
    shape checks: a whole PNG, within the size and dimension caps."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise SystemExit(f"error: {path} is not a PNG")
    width, height = struct.unpack(">II", head[16:24])
    problems = []
    if size > MAX_BYTES:
        problems.append(f"{size} bytes exceeds {MAX_BYTES}")
    if width > MAX_SIDE or height > MAX_SIDE:
        problems.append(f"{width}x{height} exceeds {MAX_SIDE}x{MAX_SIDE}")
    if problems:
        raise SystemExit(f"error: {path} fails the gate: " + "; ".join(problems))
    return width, height


def main():
    target = output_path()
    size = generate_image.write_entry(target)
    width, height = check_entry(target, size)
    print(f"wrote {target} ({size} bytes, {width}x{height} PNG)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
