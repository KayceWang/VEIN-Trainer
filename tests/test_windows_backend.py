"""真实 Windows 消息接收测试，不模拟游戏按键。"""
import sys,tempfile,ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import tkinter as tk
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hotkeys import Hotkeys,key_binding
root=tk.Tk();root.withdraw();root.update_idletasks()
with tempfile.TemporaryDirectory() as folder:
    hot=Hotkeys(Path(folder)/'keys.json')
    hot.attach(root.winfo_id())
    try:
        hot.set('toggle:test',key_binding('F10',4|0x20000))
        ident=next(iter(hot.ids))
        user=c.WinDLL('user32',use_last_error=True)
        user.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
        assert user.PostMessageW(root.winfo_id(),0x312,ident,0)
        root.update()
        assert hot.poll()==['toggle:test']
        assert hot.poll()==[]
        print('Windows RegisterHotKey + window message + queue: PASS')
    finally:hot.close()
root.destroy()
