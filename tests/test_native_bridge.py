"""Actual Windows hook/IPC, input validation and version rejection, without the game."""
import sys,os,time,struct
from pathlib import Path
from types import SimpleNamespace
import tkinter as tk
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_bridge as n
for command in ('Heal','RepairItem','SetCondition C_Exerted 0','AddXP ST_Bartering 100'):
    assert n.validate(command)==command
for command in ('Quit','Heal;Quit','Heal\nQuit','GiveItem BP_Apple 1','Heal\x00',''):
    try:n.validate(command)
    except ValueError:pass
    else:raise AssertionError(command)
root=tk.Tk();root.withdraw();root.update_idletasks()
thread=n.u.GetWindowThreadProcessId(root.winfo_id(),None)
fake=SimpleNamespace(pid=os.getpid(),base=0,unpack=lambda *_:thread,player=lambda:123,pointer=lambda _:456)
bridge=n.Bridge(fake,root.winfo_id())
try:
    bridge.submit('Heal')
    for _ in range(100):
        root.update()
        if bridge.state()==3:break
        time.sleep(.01)
    assert bridge.state()==3,'Hook did not process request'
    assert struct.unpack_from('<I',bridge.mapping,28)[0]==1,'Wrong binary must be rejected'
    try:bridge.poll()
    except OSError as error:assert '版本' in str(error)
    else:raise AssertionError('Wrong executable accepted')
    print('Actual hook + IPC + wrong-build rejection + command validation: PASS')
finally:
    bridge.close();root.destroy()
