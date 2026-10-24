"""Hotkey focus policy and toggle audio regression; never touches the game."""
import sys, os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import vein_helper as h
import hotkeys

class Value:
    def __init__(self, value): self.value=value
    def get(self): return self.value
    def set(self,value): self.value=value

runtime=Mock()
app=SimpleNamespace(hotkey_dialog=None,armed=Value(True),busy=False,
                    toggles={'无限耐力':Value(False)},connected=lambda:runtime,note=Mock())
def flip():
    value=app.toggles['无限耐力']
    value.set(not value.get())
    h.App.toggle(app,'无限耐力')
app.actions={'toggle:无限耐力':('无限耐力',flip)}
owner=[os.getpid()]
def set_owner(hwnd,pointer): pointer._obj.value=owner[0]
with patch.object(h,'user32') as user,patch.object(h,'game_windows',return_value=[200]),patch.object(h,'sound') as tone:
    user.GetWindowThreadProcessId.side_effect=set_owner
    user.GetForegroundWindow.return_value=100
    h.App.handle_hotkey(app,'toggle:无限耐力')
    assert app.toggles['无限耐力'].get() and tone.call_args.args==('on',)
    h.App.handle_hotkey(app,'toggle:无限耐力')
    assert not app.toggles['无限耐力'].get() and tone.call_args.args==('off',)
    owner[0]=12345;user.GetForegroundWindow.return_value=200
    h.App.handle_hotkey(app,'toggle:无限耐力')
    assert app.toggles['无限耐力'].get() and tone.call_args.args==('on',)
    user.GetForegroundWindow.return_value=300
    before=tone.call_count
    h.App.handle_hotkey(app,'toggle:无限耐力')
    assert tone.call_count==before
    owner[0]=os.getpid();app.armed.set(False)
    h.App.handle_hotkey(app,'toggle:无限耐力')
    assert tone.call_args.args==('error',)
with patch.object(hotkeys.winsound,'PlaySound') as play:
    for kind in ('on','off','done','error'):
        hotkeys._play_sound(kind)
        assert Path(play.call_args.args[0]).is_file()
        assert not play.call_args.args[1] & (0x00200000 | hotkeys.winsound.SND_ASYNC)
with patch.object(hotkeys.winsound,'PlaySound',side_effect=RuntimeError),patch.object(hotkeys.winsound,'Beep') as beep:
    hotkeys._play_sound('on')
    assert [call.args[0] for call in beep.call_args_list]==[740,1040]
print('Helper/game focus, other-app exclusion, ON/OFF/error sounds: PASS')
