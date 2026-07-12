import os
import json
from pathlib import Path
import subprocess
from app.config.config_loader import BEHAVIOUR_DATA

AUTO_RELOAD = BEHAVIOUR_DATA["auto_reload"]


def new_link(target_link: Path, wallpaper: Path):
    # we need to delete the old link to create a new one
    # with the same name
    if target_link.is_file():
        os.unlink(target_link)

    if wallpaper.is_file():
        # equivalent to 'ln -s wallpaper target_link'
        os.symlink(wallpaper, target_link)
    # we need to reload sway ... otherwise the wallpaper does not change...
    if AUTO_RELOAD:
        sway_reloading = subprocess.run(
            ["swaymsg", "output", '"*"', "bg", target_link, "fill"],
            capture_output=True,
            text=True,
        )
        response = None

        try:
            response = json.loads(sway_reloading.stdout)
        except json.JSONDecodeError:
            subprocess.run(
                ["notify-send", "sway-wallpi", f"stdout could not be parsed"]
            )

        if response:
            for entry in response:
                if not entry.get("success", False):
                    subprocess.run(
                        ["notify-send", "sway-wallpi", f"Reloading sway failed"]
                    )
                else:
                    subprocess.run(
                        [
                            "notify-send",
                            "sway-wallpi",
                            f"changed wallpaper to {wallpaper.name}",
                        ]
                    )
