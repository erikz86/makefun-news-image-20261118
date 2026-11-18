"""news-image-20261118 entry: a program that writes one image summing up the
world news of Wednesday 18 November 2026 to /output/entry.png.

The image is entry.png beside this file (rendered by generate_image.py from
real reporting on the day). The program just copies it: the grader runs with
no network, so the image ships in the repository. Standard library only.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

shutil.copyfile(HERE / "entry.png", OUTPUT_DIR / "entry.png")
