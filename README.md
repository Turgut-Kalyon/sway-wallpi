# sway-wallpi

A fast, terminal-based wallpaper browser with live image preview, built with Textual.

Browse your wallpaper folder with Vim-style keybindings, preview images directly in your terminal, and set your wallpaper with a single keypress — all without leaving the TTY.

## Configuration

Wallpi reads its configuration from:

```
~/.config/wallpi/config.toml
```

Example configuration:

```toml
[path]
wallpaper_dir = "~/Pictures/Wallpapers"
target_dir = "~/.config/wallpi/current_wallpaper"

[behaviour]
auto_reload = true
```

## License

[MIT](LICENSE)
