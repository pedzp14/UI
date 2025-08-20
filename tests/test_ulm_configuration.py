import importlib.util
import json
from pathlib import Path
import sys
import types

import pytest

# Stub external dependencies required by base.py
aiogithubapi = types.ModuleType("aiogithubapi")
aiogithubapi.GitHubAPI = object
aiogithubapi.GitHubAuthenticationException = Exception
aiogithubapi.GitHubException = Exception
aiogithubapi.GitHubNotModifiedException = Exception
aiogithubapi.GitHubRatelimitException = Exception
sys.modules["aiogithubapi"] = aiogithubapi

# Stub homeassistant package structure
homeassistant = types.ModuleType("homeassistant")
components = types.ModuleType("homeassistant.components")
frontend = types.ModuleType("homeassistant.components.frontend")
frontend.add_extra_js_url = lambda *args, **kwargs: None
frontend.async_remove_panel = lambda *args, **kwargs: None
lovelace = types.ModuleType("homeassistant.components.lovelace")
lovelace._register_panel = lambda *args, **kwargs: None
dashboard = types.ModuleType("homeassistant.components.lovelace.dashboard")


class LovelaceYAML:  # pylint: disable=too-few-public-methods
    pass


dashboard.LovelaceYAML = LovelaceYAML
config_entries = types.ModuleType("homeassistant.config_entries")


class ConfigEntry:  # pylint: disable=too-few-public-methods
    pass


class ConfigEntryState:  # pylint: disable=too-few-public-methods
    pass


config_entries.ConfigEntry = ConfigEntry
config_entries.ConfigEntryState = ConfigEntryState
core = types.ModuleType("homeassistant.core")


class HomeAssistant:  # pylint: disable=too-few-public-methods
    pass


core.HomeAssistant = HomeAssistant
loader = types.ModuleType("homeassistant.loader")


class Integration:  # pylint: disable=too-few-public-methods
    file_path = ""


loader.Integration = Integration

homeassistant.components = components
components.frontend = frontend
components.lovelace = lovelace

sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.components"] = components
sys.modules["homeassistant.components.frontend"] = frontend
sys.modules["homeassistant.components.lovelace"] = lovelace
sys.modules["homeassistant.components.lovelace.dashboard"] = dashboard
sys.modules["homeassistant.config_entries"] = config_entries
sys.modules["homeassistant.core"] = core
sys.modules["homeassistant.loader"] = loader

# Prepare package structure for custom_components
package_root = (
    Path(__file__).resolve().parents[1] / "custom_components" / "ui_lovelace_minimalist"
)
custom_components_pkg = types.ModuleType("custom_components")
custom_components_pkg.__path__ = [
    str(Path(__file__).resolve().parents[1] / "custom_components")
]
sys.modules["custom_components"] = custom_components_pkg
ulm_pkg = types.ModuleType("custom_components.ui_lovelace_minimalist")
ulm_pkg.__path__ = [str(package_root)]
sys.modules["custom_components.ui_lovelace_minimalist"] = ulm_pkg

# Load const and enums modules
const_path = package_root / "const.py"
const_spec = importlib.util.spec_from_file_location(
    "custom_components.ui_lovelace_minimalist.const", const_path
)
const_module = importlib.util.module_from_spec(const_spec)
sys.modules["custom_components.ui_lovelace_minimalist.const"] = const_module
const_spec.loader.exec_module(const_module)

enums_path = package_root / "enums.py"
enums_spec = importlib.util.spec_from_file_location(
    "custom_components.ui_lovelace_minimalist.enums", enums_path
)
enums_module = importlib.util.module_from_spec(enums_spec)
sys.modules["custom_components.ui_lovelace_minimalist.enums"] = enums_module
enums_spec.loader.exec_module(enums_module)

# Load base module
BASE_PATH = package_root / "base.py"
spec = importlib.util.spec_from_file_location(
    "custom_components.ui_lovelace_minimalist.base", BASE_PATH
)
base = importlib.util.module_from_spec(spec)
sys.modules["custom_components.ui_lovelace_minimalist.base"] = base
spec.loader.exec_module(base)
UlmConfiguration = base.UlmConfiguration


def test_to_json_returns_string():
    config = UlmConfiguration()
    json_str = config.to_json()
    assert isinstance(json_str, str)  # nosec
    assert json.loads(json_str) == config.to_dict()  # nosec


def test_update_from_dict_updates_fields():
    config = UlmConfiguration()
    data = {"language": "es", "theme": "dark"}
    config.update_from_dict(data)
    assert config.language == "es"  # nosec
    assert config.theme == "dark"  # nosec


def test_update_from_dict_raises_on_non_dict():
    config = UlmConfiguration()
    with pytest.raises(Exception):
        config.update_from_dict("not a dict")
