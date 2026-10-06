import pytest
import yaml
from pydantic import ValidationError

from reviewer.config import load_config


def test_missing_file_uses_defaults(tmp_path):
    config = load_config(tmp_path / "missing.yml")

    assert config.max_diff_chars == 50000
    assert config.ignored_paths == []


def test_empty_file_uses_defaults(tmp_path):
    path = tmp_path / ".reviewer.yml"
    path.write_text("", encoding="utf-8")

    config = load_config(path)

    assert config.max_diff_chars == 50000
    assert config.ignored_paths == []


def test_loads_custom_settings(tmp_path):
    path = tmp_path / ".reviewer.yml"
    path.write_text(
        "max_diff_chars: 1000\n"
        "ignored_paths:\n"
        '  - "*.lock"\n'
        '  - "dist/**"\n',
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.max_diff_chars == 1000
    assert config.ignored_paths == ["*.lock", "dist/**"]


@pytest.mark.parametrize("limit", [0, -1])
def test_rejects_nonpositive_limit(tmp_path, limit):
    path = tmp_path / ".reviewer.yml"
    path.write_text(
        f"max_diff_chars: {limit}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(path)


def test_rejects_ignored_paths_as_string(tmp_path):
    path = tmp_path / ".reviewer.yml"
    path.write_text(
        'ignored_paths: "*.lock"\n',
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(path)


def test_rejects_non_mapping_config(tmp_path):
    path = tmp_path / ".reviewer.yml"
    path.write_text("- unexpected\n- list\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        load_config(path)


def test_rejects_malformed_yaml(tmp_path):
    path = tmp_path / ".reviewer.yml"
    path.write_text("ignored_paths: [\n", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        load_config(path)