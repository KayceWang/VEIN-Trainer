"""Find the installed Steam copy without machine-specific paths."""
import os
from pathlib import Path
import re
import winreg

GAME_RELATIVE=Path('steamapps/common/Vein/Vein/Binaries/Win64/Vein-Win64-Test.exe')


def find_game():
    override=os.environ.get('VEIN_GAME_EXE')
    if override:
        return Path(override).expanduser().resolve()
    roots=[Path(os.environ.get('ProgramFiles(x86)',r'C:\Program Files (x86)'))/'Steam']
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Valve\Steam') as key:
            roots.insert(0,Path(winreg.QueryValueEx(key,'SteamPath')[0]))
    except OSError:
        pass
    for root in list(roots):
        libraries=root/'steamapps/libraryfolders.vdf'
        try:
            text=libraries.read_text(encoding='utf-8')
        except OSError:
            continue
        roots.extend(Path(value.replace('\\\\','\\')) for value in re.findall(r'"path"\s*"([^"]+)"',text))
    for root in roots:
        candidate=root/GAME_RELATIVE
        if candidate.is_file():
            return candidate
    return roots[0]/GAME_RELATIVE
