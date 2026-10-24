import os,sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from game_path import find_game,GAME_RELATIVE

with tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    steam=root/'Steam';library=root/'Library'
    (steam/'steamapps').mkdir(parents=True)
    game=library/GAME_RELATIVE
    game.parent.mkdir(parents=True);game.write_bytes(b'test')
    (steam/'steamapps/libraryfolders.vdf').write_text('"path" "'+str(library).replace('\\','\\\\')+'"',encoding='utf-8')
    with patch.dict(os.environ,{'ProgramFiles(x86)':folder},clear=True),patch('game_path.winreg.OpenKey',side_effect=OSError):
        assert find_game()==game
    with patch.dict(os.environ,{'VEIN_GAME_EXE':str(game)}):
        assert find_game()==game.resolve()
print('Steam library discovery and explicit game path override: PASS')
