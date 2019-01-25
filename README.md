# gimp-superxBR
A GIMP Python plugin for integer scaling pixel art to higher resolutions using Hyllian's Super-xBR algorithm.

Hooks into the GIMP-Python API to display progress and request a custom scale factor.

Adapted from Hyllian's C++ version of Super-xBR - https://pastebin.com/cbH8ZQQT

# Installation

Add superxBR.py to the directory where your GIMP plugins are located:

1. Download this repository and extract it

2. Open GIMP

3. Edit >> Preferences

4. In the Folders dropdown on the left, find the Plugins tab.

![img](https://i.imgur.com/Sff22K4.png)

5. Highlight one of the directories and click the top right button ("Show file location in the file manager").

6. Drag superxBR.py into the directory, then restart GIMP. You will find the plugin in Filters >> Enhance >> Super-xBR(py).

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

GIMP-Python, a wrapper API for various C functions in libgimp, created by James Henstridge.
