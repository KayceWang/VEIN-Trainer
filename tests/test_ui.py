import sys
from pathlib import Path
import tkinter as tk
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import vein_helper as h
from trainer_ui import Switch
root=tk.Tk();root.withdraw()
app=h.App(root)
def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)
try:
    assert not app.armed.get()
    assert any(isinstance(widget,tk.Label) and widget.cget('text')=='请先进入游戏世界' for widget in descendants(root))
    assert all(not value.get() for value in app.toggles.values())
    switches=[widget for widget in descendants(root) if isinstance(widget,Switch)]
    assert len(switches)==6
    assert all(widget.itemcget(widget.action_label,'text')=='开启' for widget in switches)
    app.toggles['无限耐力'].set(True)
    assert sum(widget.itemcget(widget.action_label,'text')=='关闭' for widget in switches)==2
    app.toggles['无限耐力'].set(False)
    assert all(widget.itemcget(widget.action_label,'text')=='开启' for widget in switches)
    assert 'toggle:无限耐力' in app.actions and 'RepairItem' in app.actions
    assert len(app.fields['TeleportTo'][2])==291
    app.armed.set(True)
    assert app.play_button.itemcget(app.play_button.label,'text')=='正在运行   ×'
    app.armed.set(False)
    print('Single page + default OFF + two linked stamina switches + PLAY state: PASS')
finally:app.close()
