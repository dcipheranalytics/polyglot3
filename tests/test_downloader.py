"""Downloader tests against a local HTTP server serving an index built by tools/data/build_index.py."""

import functools
import json
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import pytest

from polyglot.downloader import Downloader

sys.path.insert(0, str(Path(__file__).parents[1] / "tools" / "data"))
from build_index import build_index  # noqa: E402


class QuietHandler(SimpleHTTPRequestHandler):
  def log_message(self, *args):
    pass


@pytest.fixture
def server(tmp_path):
  root = tmp_path / "server"
  for name, content in [("ner2/xx/xx_ner.pkl.tar.bz2", b"ner model"),
                        ("pos2/xx/xx_pos.pkl.tar.bz2", b"pos model"),
                        ("ner2/yy/yy_ner.pkl.tar.bz2", b"other language")]:
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_bytes(content)
  (root / "index.json").write_text(json.dumps(build_index(root)))

  httpd = HTTPServer(("127.0.0.1", 0),
                     functools.partial(QuietHandler, directory=str(root)))
  thread = threading.Thread(target=httpd.serve_forever, daemon=True)
  thread.start()
  yield root, "http://127.0.0.1:{}/".format(httpd.server_port)
  httpd.shutdown()
  httpd.server_close()


def test_download_package(server, tmp_path):
  root, url = server
  d = Downloader(server_index_url=url, download_dir=str(tmp_path / "data"))
  assert d.download("ner2.xx", quiet=True, raise_on_error=True)
  assert (tmp_path / "data/ner2/xx/xx_ner.pkl.tar.bz2").read_bytes() == b"ner model"
  assert d.status("ner2.xx") == Downloader.INSTALLED
  assert d.status("pos2.xx") == Downloader.NOT_INSTALLED


def test_download_language_collection(server, tmp_path):
  root, url = server
  d = Downloader(server_index_url=url.rstrip("/"), download_dir=str(tmp_path / "data"))
  assert d.download("LANG:xx", quiet=True, raise_on_error=True)
  assert d.status("LANG:xx") == Downloader.INSTALLED
  assert d.status("ner2.yy") == Downloader.NOT_INSTALLED


def test_checksum_mismatch_removes_file(server, tmp_path):
  root, url = server
  (root / "ner2/xx/xx_ner.pkl.tar.bz2").write_bytes(b"tampered!")  # same size, different content
  d = Downloader(server_index_url=url, download_dir=str(tmp_path / "data"))
  with pytest.raises(ValueError, match="Checksum mismatch"):
    d.download("ner2.xx", quiet=True, raise_on_error=True)
  assert not (tmp_path / "data/ner2/xx/xx_ner.pkl.tar.bz2").exists()


def test_default_url_from_environment():
  # DEFAULT_URL is read at import time; check the override in a fresh interpreter.
  import subprocess
  out = subprocess.run(
      [sys.executable, "-c", "from polyglot.downloader import Downloader; print(Downloader.DEFAULT_URL)"],
      env={"POLYGLOT_DATA_URL": "https://example.org/data/", "PATH": ""},
      capture_output=True, text=True, check=True)
  assert out.stdout.strip() == "https://example.org/data/"
