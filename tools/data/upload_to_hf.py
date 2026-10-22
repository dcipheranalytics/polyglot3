#!/usr/bin/env python
"""Upload a polyglot_data directory (with its index.json) to a Hugging Face dataset repo.

Requires `pip install huggingface_hub` and a write token (`hf auth login`).

Usage: python tools/data/upload_to_hf.py path/to/polyglot_data polyglot3/polyglot3-data
"""

import sys
from pathlib import Path

from huggingface_hub import HfApi


def main(root, repo_id):
  if not (Path(root) / "index.json").exists():
    sys.exit("index.json missing; run tools/data/build_index.py first")
  api = HfApi()
  api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
  api.upload_folder(repo_id=repo_id, repo_type="dataset", folder_path=root,
                    commit_message="Upload polyglot models")


if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
