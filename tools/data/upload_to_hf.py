#!/usr/bin/env python
"""Upload a polyglot_data directory (with its index.json) to a Hugging Face dataset repo.

Requires `pip install huggingface_hub` and a write token (`hf auth login`).

The dataset card (tools/data/DATASET_CARD.md) is uploaded as README.md.

Usage: python tools/data/upload_to_hf.py path/to/polyglot_data dcipheranalytics/polyglot3
       python tools/data/upload_to_hf.py --card-only dcipheranalytics/polyglot3
"""

import sys
from pathlib import Path

from huggingface_hub import HfApi


CARD = Path(__file__).with_name("DATASET_CARD.md")


def upload_card(api, repo_id):
  api.upload_file(path_or_fileobj=str(CARD), path_in_repo="README.md",
                  repo_id=repo_id, repo_type="dataset",
                  commit_message="Update dataset card")


def main(root, repo_id):
  if not (Path(root) / "index.json").exists():
    sys.exit("index.json missing; run tools/data/build_index.py first")
  api = HfApi()
  api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
  api.upload_folder(repo_id=repo_id, repo_type="dataset", folder_path=root,
                    commit_message="Upload polyglot models")
  upload_card(api, repo_id)


if __name__ == "__main__":
  if sys.argv[1] == "--card-only":
    upload_card(HfApi(), sys.argv[2])
  else:
    main(sys.argv[1], sys.argv[2])
