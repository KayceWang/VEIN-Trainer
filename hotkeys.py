"""Windows 注册快捷键；不安装键盘钩子、不记录输入。"""
import ctypes as c
from ctypes import wintypes as w
import json
from pathlib import Path
import winsound
import threading
from collections import deque

u = c.WinDLL('user32', use_last_error=True)
u.RegisterHotKey.argtypes = [w.HWND, c.c_int, w.UINT, w.UINT]
u.UnregisterHotKey.argtypes = [w.HWND, c.c_int]
u.PeekMessageW.argtypes = [c.POINTER(w.MSG), w.HWND, w.UINT, w.UINT, w.UINT]
LRESULT = c.c_ssize_t
WNDPROC = c.WINFUNCTYPE(LRESULT, w.HWND, w.UINT, w.WPARAM, w.LPARAM)
u.SetWindowLongPtrW.argtypes = [w.HWND, c.c_int, c.c_void_p]
u.SetWindowLongPtrW.restype = c.c_void_p
u.CallWindowProcW.argtypes = [c.c_void_p, w.HWND, w.UINT, w.WPARAM, w.LPARAM]
u.CallWindowProcW.restype = LRESULT


def key_binding(keysym, state):
    modifiers = (2 if state & 4 else 0) | (1 if state & 0x20000 else 0) | (4 if state & 1 else 0)
    key = keysym.upper()
    if key.startswith('F') and key[1:].isdigit() and 1 <= int(key[1:]) <= 12:
        vk = 0x70 + int(key[1:]) - 1
    elif len(key) == 1 and key.isascii() and key.isalnum() and modifiers:
        vk = ord(key)
    else:
        raise ValueError('请用 F1–F12，或 Ctrl / Alt / Shift 加字母、数字。')
    if modifiers == 4 and vk < 0x70:
        raise ValueError('普通字母请搭配 Ctrl 或 Alt，避免打字时误触。')
    label = '+'.join([name for mask, name in ((2, 'Ctrl'), (1, 'Alt'), (4, 'Shift')) if modifiers & mask] + [key])
    return {'modifiers':modifiers, 'vk':vk, 'label':label}


def valid_binding(value):
    return (isinstance(value, dict) and type(value.get('modifiers')) is int
            and value['modifiers'] in range(8) and type(value.get('vk')) is int
            and (0x70 <= value['vk'] <= 0x7b or
                 value['modifiers'] & 3 and (0x30 <= value['vk'] <= 0x39 or 0x41 <= value['vk'] <= 0x5a))
            and isinstance(value.get('label'), str) and len(value['label']) <= 30)


class Hotkeys:
    def __init__(self, path):
        self.path = Path(path)
        self.bindings = {}
        self.ids = {}
        self.next_id = 1
        self.hwnd = None
        self.queue = deque()

    def attach(self, hwnd):
        self.hwnd = hwnd
        @WNDPROC
        def procedure(window, message, wp, lp):
            if message == 0x312:
                action = self.ids.get(wp)
                if action:
                    self.queue.append(action)
                return 0
            return u.CallWindowProcW(self.previous, window, message, wp, lp)
        self.procedure = procedure
        self.previous = u.SetWindowLongPtrW(hwnd, -4, c.cast(procedure, c.c_void_p))
        if not self.previous:
            raise c.WinError(c.get_last_error())

    def set(self, action, binding):
        if binding is not None and not valid_binding(binding):
            raise ValueError('快捷键配置无效。')
        if binding:
            for other, old in self.bindings.items():
                if other != action and (old['modifiers'], old['vk']) == (binding['modifiers'], binding['vk']):
                    raise ValueError('该快捷键已分配给另一项功能。')
            candidate = self.next_id
            if not u.RegisterHotKey(self.hwnd, candidate, binding['modifiers'] | 0x4000, binding['vk']):
                raise OSError('该快捷键已被系统或其他程序占用，请换一个。')
            self.next_id += 1
        old_id = next((key for key, name in self.ids.items() if name == action), None)
        if old_id is not None:
            u.UnregisterHotKey(self.hwnd, old_id)
            del self.ids[old_id]
        if binding:
            self.ids[candidate] = action
            self.bindings[action] = binding
        else:
            self.bindings.pop(action, None)

    def save(self):
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.bindings, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(self.path)

    def load(self, actions):
        errors = []
        if not self.path.exists():
            return errors
        try:
            saved = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(saved, dict):
                raise ValueError('配置不是对象')
            for action, binding in saved.items():
                if action in actions:
                    try:
                        self.set(action, binding)
                    except (ValueError, OSError) as error:
                        errors.append(f'{actions[action][0]}：{error}')
        except (ValueError, OSError) as error:
            errors.append('快捷键配置读取失败：' + str(error))
        return errors

    def poll(self):
        actions = list(self.queue)
        self.queue.clear()
        return actions

    def close(self):
        for ident in self.ids:
            u.UnregisterHotKey(self.hwnd, ident)
        self.ids.clear()
        if self.hwnd and getattr(self, 'previous', None):
            u.SetWindowLongPtrW(self.hwnd, -4, self.previous)
            self.hwnd = None


_sound_lock = threading.Lock()


def _play_sound(kind):
    try:
        path=Path(__file__).parent / 'sounds' / (kind + '.wav')
        if not path.is_file():raise RuntimeError('Missing sound file')
        # Use the app audio session; synchronous playback keeps rapid toggles audible.
        winsound.PlaySound(str(path),winsound.SND_FILENAME | winsound.SND_NODEFAULT)
    except (RuntimeError,OSError):
        notes={'on':(740,1040),'off':(620,370),'done':(800,),'error':(240,200)}[kind]
        for frequency in notes:
            try:winsound.Beep(frequency,140)
            except RuntimeError:break


def sound(kind):
    def play():
        with _sound_lock:
            _play_sound(kind)
    threading.Thread(target=play,daemon=True).start()
