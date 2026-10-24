"""Use the game's own Exec on its main thread, without console or keyboard input."""
import ctypes as c
from ctypes import wintypes as w
import mmap
from pathlib import Path
import re
import struct
import time

MAGIC=0x5645494e
MESSAGE=0x8000+0x4a1
COMMANDS=frozenset(('Heal HealEveryone RepairItem LearnEveryRecipe LearnEveryBuildObject '
    'AddXP SetCondition GiveKey SetTiresPunctured Unlock Lockpick SetWeather ClearWeather '
    'DiscoverEveryLocation RemoveAllCorpses RandomizeTime AddTime TeleportTo SpawnHorde').split())
u=c.WinDLL('user32',use_last_error=True)
k=c.WinDLL('kernel32',use_last_error=True)
u.SetWindowsHookExW.argtypes=[c.c_int,c.c_void_p,w.HINSTANCE,w.DWORD]
u.SetWindowsHookExW.restype=w.HANDLE
u.UnhookWindowsHookEx.argtypes=[w.HANDLE]
u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
u.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)]
k.CreateMutexW.argtypes=[c.c_void_p,w.BOOL,w.LPCWSTR]
k.CreateMutexW.restype=w.HANDLE
k.CloseHandle.argtypes=[w.HANDLE]


def validate(command):
    if (not isinstance(command,str) or not command or len(command)>500 or
        not re.fullmatch(r'[A-Za-z0-9_.+ -]+',command) or command.split()[0] not in COMMANDS):
        raise ValueError('不支持的直接操作。')
    return command


class Bridge:
    def __init__(self,runtime,hwnd):
        self.runtime=runtime
        self.hwnd=hwnd
        self.hook=None
        self.mapping=None
        self.mutex=None
        pid=w.DWORD()
        thread=u.GetWindowThreadProcessId(hwnd,c.byref(pid))
        if pid.value!=runtime.pid or thread!=runtime.unpack(runtime.base+0xaf4e108,'<I'):
            raise OSError('游戏线程不匹配，已停止直接操作。')
        try:
            self.mutex=k.CreateMutexW(None,False,f'Local\\VEINTrainerNativeOwner_{runtime.pid}')
            if not self.mutex: raise c.WinError(c.get_last_error())
            if c.get_last_error()==183: raise OSError('另一个修改器窗口已连接，请先关闭旧窗口。')
            self.mapping=mmap.mmap(-1,4096,tagname=f'Local\\VEINTrainerNative_{runtime.pid}')
            self.mapping[:4096]=bytes(4096)
            self.module=c.WinDLL(str(Path(__file__).with_name('vein_native.dll')))
            self.hook=u.SetWindowsHookExW(3,c.cast(self.module.TrainerHook,c.c_void_p),self.module._handle,thread)
            if not self.hook: raise c.WinError(c.get_last_error())
        except Exception:
            self.close()
            raise

    def submit(self,command):
        command=validate(command)
        if not self.hook: raise OSError('游戏连接已关闭。')
        if self.state() in (1,2): raise OSError('上一项操作仍在执行，请稍候。')
        pawn=self.runtime.player()
        world=self.runtime.pointer(self.runtime.base+0xb2186b8)
        raw=command.encode('utf-16-le')+b'\0\0'
        self.mapping[:40]=struct.pack('<IIQQIIII',MAGIC,0,world,pawn,0,0,0,0)
        self.mapping[40:1064]=raw.ljust(1024,b'\0')
        self.mapping[4:8]=struct.pack('<I',1)
        if not u.PostMessageW(self.hwnd,MESSAGE,MAGIC,0):
            self.mapping[4:8]=bytes(4)
            raise c.WinError(c.get_last_error())
        self.deadline=time.monotonic()+8

    def state(self):
        return struct.unpack_from('<I',self.mapping,4)[0]

    def poll(self):
        state=self.state()
        if state==3:
            result,error,thread=struct.unpack_from('<III',self.mapping,24)
            self.mapping[4:8]=bytes(4)
            if error:
                raise OSError({1:'游戏版本不匹配。',2:'游戏线程不匹配。',3:'角色或世界已变化，请重新连接。',
                               4:'不支持的直接操作。',5:'游戏日志组件尚未就绪。'}.get(error,'直接操作失败。'))
            if not result: raise OSError('游戏未接受这项操作，请检查目标及当前世界。')
            return True
        if time.monotonic()>self.deadline:
            raise OSError('游戏操作尚未确认，请勿重复执行或切换存档。')
        return False

    def close(self):
        if self.hook:
            u.UnhookWindowsHookEx(self.hook)
            self.hook=None
        if self.mapping:
            self.mapping.close()
            self.mapping=None
        if self.mutex:
            k.CloseHandle(self.mutex)
            self.mutex=None
