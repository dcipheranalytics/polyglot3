#!/usr/bin/env python
"""Build the downloader's index.json for a local polyglot_data directory.

The index mimics a Cloud Storage object listing ({"items": [...]}) without
URLs, so the downloader resolves each package relative to wherever the
index is hosted.

Usage: python tools/data/build_index.py path/to/polyglot_data
"""

import base64
import hashlib
import json
import sys
from pathlib import Path


def md5_base64(filename):
    digest = hashlib.md5()
    with open(filename, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return base64.b64encode(digest.digest()).decode("ascii")


def build_index(root):
    root = Path(root)
    items = []
    # Packages live at <task>/<lang>/<file>, one file per package.
    for f in sorted(root.glob("*/*/*")):
        if f.is_file():
            items.append(
                {
                    "name": f.relative_to(root).as_posix(),
                    "size": f.stat().st_size,
                    "md5Hash": md5_base64(f),
                }
            )
    return {"items": items}


def main(root):
    index = build_index(root)
    with open(Path(root) / "index.json", "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1)
    print("{} packages indexed".format(len(index["items"])))


if __name__ == "__main__":
    main(sys.argv[1])
