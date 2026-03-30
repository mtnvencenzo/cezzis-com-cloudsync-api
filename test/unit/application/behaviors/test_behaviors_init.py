# Unit tests for application/behaviors/__init__.py
import importlib


def test_import_behaviors_init():
    importlib.import_module("cezzis_com_cloudsync_api.application.behaviors")
