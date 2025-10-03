import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from mdxscraper.services.version_check_service import VersionCheckService


class _FakeResponse:
	def __init__(self, payload: dict, status: int = 200):
		self._data = json.dumps(payload).encode()
		self.status = status

	def read(self):
		return self._data

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc, tb):
		return False


def test_check_for_updates_latest_version(monkeypatch):
	service = VersionCheckService()

	# Mock version helpers
	monkeypatch.setattr("mdxscraper.services.version_check_service.get_version", lambda: "5.0.0")
	monkeypatch.setattr("mdxscraper.services.version_check_service.compare_version", lambda v: 0)

	# Mock urllib.request.urlopen
	payload = {"tag_name": "v5.0.0"}
	fake_resp = _FakeResponse(payload)
	monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=10: fake_resp)

	is_latest, message, latest = service.check_for_updates()
	assert is_latest is True
	assert latest == "5.0.0"
	assert "latest" in message.lower()
	assert service.get_latest_version() == "5.0.0"
	assert service.get_last_error() is None


def test_check_for_updates_newer_available(monkeypatch):
	service = VersionCheckService()

	monkeypatch.setattr("mdxscraper.services.version_check_service.get_version", lambda: "5.0.0")
	# compare_version < 0 means current is older
	monkeypatch.setattr("mdxscraper.services.version_check_service.compare_version", lambda v: -1)

	payload = {"tag_name": "v5.1.0"}
	fake_resp = _FakeResponse(payload)
	monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=10: fake_resp)

	is_latest, message, latest = service.check_for_updates()
	assert is_latest is False
	assert latest == "5.1.0"
	assert "new version" in message.lower()


def test_check_for_updates_network_error(monkeypatch):
	service = VersionCheckService()

	class _UrlError(Exception):
		pass

	# Patch the specific error class lookup used in code path
	monkeypatch.setattr("urllib.error.URLError", _UrlError)

	def raise_error(req, timeout=10):
		raise _UrlError("network down")

	monkeypatch.setattr("urllib.request.urlopen", raise_error)

	is_latest, message, latest = service.check_for_updates()
	assert is_latest is False
	assert latest is None
	assert "failed" in message.lower()
	assert service.get_last_error() is not None


def test_check_for_updates_bad_json(monkeypatch):
	service = VersionCheckService()

	class _BadResponse:
		def read(self):
			return b"{bad json}"
		def __enter__(self):
			return self
		def __exit__(self, *a):
			return False

	monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=10: _BadResponse())

	is_latest, message, latest = service.check_for_updates()
	assert is_latest is False
	assert latest is None
	assert "parse" in message.lower() or "error" in message.lower()
