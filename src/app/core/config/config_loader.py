import toml
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "wallpi" / "config.toml"

data = toml.load(CONFIG_PATH)

PATH_DATA = data["path"]
BEHAVIOUR_DATA = data["behaviour"]
