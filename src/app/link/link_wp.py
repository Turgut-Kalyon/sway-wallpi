import os
from pathlib import Path
import shutil
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
        sway_reloading = exec_set_wallpaper(target_link)

        if sway_reloading.returncode != 0:
            subprocess.run(["notify-send", "sway-wallpi", f"Changing Wallpaper failed"])
        else:
            subprocess.run(
                [
                    "notify-send",
                    "sway-wallpi",
                    f"changed wallpaper to {wallpaper.name}",
                ]
            )


def exec_set_wallpaper(target_link: Path):
    process = None
    if shutil.which("awww") or shutil.which("swww"):
        wallpaper_bin = "awww" if shutil.which("awww") else "swww"
        daemon_bin = "awww-daemon" if shutil.which("awww-daemon") else "swww-daemon"
        if not is_running(daemon_bin):
            raise RuntimeError(
                f"{daemon_bin} is not running, write 'exec {daemon_bin}' in your config file."
            )
        process = subprocess.run(
            [wallpaper_bin, "img", target_link], capture_output=True, text=True
        )
    elif shutil.which("swaymsg") and shutil.which("swaybg"):
        process = subprocess.run(
            ["swaymsg", "output", "*", "bg", target_link, "fill"],
            capture_output=True,
            text=True,
        )
    elif shutil.which("swaybg"):
        process = subprocess.run(
            ["swaybg", "-o", "*", "-i", target_link, "-m", "fill"],
            capture_output=True,
            text=True,
        )
    else:
        raise RuntimeError(
            "There are no capable wallpaper tools. Please install swww, awww or swaybg"
        )
    return process


def is_running(process_name: str) -> bool:
    result = subprocess.run(
        ["pgrep", "-x", process_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0
