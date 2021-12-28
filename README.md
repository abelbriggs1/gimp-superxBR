# gimp-superxBR

A GIMP Python plugin for integer scaling pixel art to higher resolutions using Hyllian's super-xBR algorithm.

Hooks into the GIMP-Python API to display progress and request a custom scale factor.

Adapted from Hyllian's C++ version of Super-xBR - https://pastebin.com/cbH8ZQQT

# Compatibility

**This plugin currently only supports Python 2/GIMP 2.x**. GIMP 3 has massive
API changes and uses Python 3, so a porting effort will be necessary.

This plugin requires your GIMP distribution to package `gimp-python` support.
You can check this by clicking the `Filters` drop-down in GIMP - if the
`Python-Fu` menu exists near the bottom, you are good to go.

Most GIMP installations package `gimp-python` by default. As of GIMP 2.10, however,
due to Python 2 end-of-life, there have been several distributions/releases with
missing Python support.

If `Python-Fu` does not exist in `Filters`, please try the following in order:

- **Linux**: If you installed GIMP via your distribution's package
  manager, please uninstall and try a portable installation. The easiest
  method is to install the official Flatpak.
- **Windows**: If you already had Python installed before installing GIMP,
  please try uninstalling all Python versions and GIMP, then installing
  GIMP again on its own. If `Python-Fu` shows up now, you should be able
  to install your independent Python versions on top of GIMP without issue.
- As a last resort, try reverting to GIMP 2.8, which was the latest stable
  version before the Python 2 end-of-life debacle.

# Installation

Please make sure you have read the [`Compatibility`](#compatibility) section and have access to
the `Filters >> Python-Fu` menu in GIMP before continuing.

To install, add `superxBR.py` to the directory where your GIMP plugins are located.

1. Download this repository and extract it

2. Open GIMP

3. `Edit >> Preferences`

4. In the `Folders` dropdown on the left, find the `Plugins` tab.

![img](https://i.imgur.com/Sff22K4.png)

5. Highlight one of the directories and click the top right button (`Show file location in the file manager`).

6. Drag `superxBR.py` into the directory, then restart GIMP. You should find the plugin in `Filters >> Enhance >> Super-xBR(py)`.

# Examples

| Original image        | Scaled 2x (same size) |
| ------------- |-------------|
| <img src=https://i.imgur.com/GLFpO76.png height="192"/> | <img src=https://i.imgur.com/WMktwGw.png height="192"/> |
| <img src=https://i.imgur.com/WN535Hm.png height="240"/> | <img src=https://i.imgur.com/6XkhkLt.png height="240"/> |

| Original image        | Scaled 2x (full size) |
| ------------- |-------------|
| <img src=https://i.imgur.com/GLFpO76.png height="192"/> | <img src=https://i.imgur.com/WMktwGw.png/> |
| <img src=https://i.imgur.com/WN535Hm.png height="240"/> | <img src=https://i.imgur.com/6XkhkLt.png/> |

# License

This project is licensed under the MIT License. See LICENSE.md for more detail.

# Acknowledgments

Hyllian for their Super-xBR algorithm and reference PDF/C++ code.

GIMP-Python, a wrapper API for various C functions in `libgimp`, created by James Henstridge.
