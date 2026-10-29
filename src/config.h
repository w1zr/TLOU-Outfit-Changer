// Settings read from TLOUOutfitChanger.ini next to the game executable.
// A missing file or key falls back to the defaults below.
#pragma once

struct Config {
    bool unlockAllSkins = true; // Skins menus open and every skin owned
    bool logging = true;
};

Config LoadConfig(const wchar_t* iniPath);
