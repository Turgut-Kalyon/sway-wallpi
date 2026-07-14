import os
from pathlib import Path
import shutil
import subprocess
from app.config.config_loader import BEHAVIOUR_DATA

AUTO_RELOAD = BEHAVIOUR_DATA["auto_reload"]


def new_link(target_link: Path, wallpaper: Path):
    """Update the wallpaper symlink and optionally reload the wallpaper.

    Removes the existing symbolic link (if present), creates a new one
    pointing to the selected wallpaper, and optionally reloads the wallpaper
    using the configured wallpaper backend.

    Args:
        target_link: Path of the symbolic link to create or replace.
        wallpaper: Path to the wallpaper image.
    """

    if target_link.is_file():
        os.unlink(target_link)

    if wallpaper.is_file():
        os.symlink(wallpaper, target_link)

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
    """Set the current wallpaper using the first available backend.

    The function prefers `awww`/`swww` if available. If neither is installed,
    it falls back to `swaymsg` or `swaybg`.

    Args:
        target_link: Symbolic link pointing to the wallpaper image.

    Returns:
        The completed subprocess representing the wallpaper command.

    Raises:
        RuntimeError: If the required wallpaper daemon is not running or
            if no supported wallpaper tool is installed.
    """
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
    """Check whether a process with the given name is running.

    Args:
        process_name: Name of the process to search for.

    Returns:
        True if the process is running, otherwise False.
    """
    result = subprocess.run(
        ["pgrep", "-x", process_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0
