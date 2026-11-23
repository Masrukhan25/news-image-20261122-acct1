"""Copy entry.png to the output directory, byte-identical.

Reads the entry image next to this script and writes it to
MAKEFUN_OUTPUT_DIR (default /output) as entry.png.
Standard library only; no network, no randomness.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
