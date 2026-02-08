import sys
from pathlib import Path

# Ensure repository root is on sys.path so `flows` package is importable during tests
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from flows.utils import get_additional_env_vars_for_container


def test_returns_mapping_when_file_exists(tmp_path, monkeypatch):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    file = conf_dir / "container-env.yml"
    data = {"FOO": "bar", "BAZ": "qux"}
    file.write_text(yaml.safe_dump(data))

    monkeypatch.chdir(tmp_path)

    result = get_additional_env_vars_for_container()

    assert result == data


def test_returns_empty_dict_when_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = get_additional_env_vars_for_container()

    assert result == {}


def test_skips_non_mapping_and_logs_warning(tmp_path, monkeypatch, caplog):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    file = conf_dir / "container-env.yml"
    # write a YAML sequence instead of a mapping
    file.write_text(yaml.safe_dump(["a", "b"]))

    monkeypatch.chdir(tmp_path)

    with caplog.at_level("WARNING"):
        result = get_additional_env_vars_for_container()

    assert result == {}
    assert any("does not contain a mapping" in rec.message for rec in caplog.records)
