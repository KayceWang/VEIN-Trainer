"""VEIN修改器：游戏原生指令与已核对版本的单机状态控制。"""
from __future__ import annotations

import ctypes
from ctypes import wintypes as w
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
import tkinter as tk
from tkinter import messagebox, ttk
from items_catalog import ITEMS
from game_options import STATS, CONDITIONS, LOCATIONS
from runtime_state import Runtime
from hotkeys import Hotkeys, key_binding, sound
from native_bridge import Bridge, COMMANDS as DIRECT_COMMANDS
from game_path import find_game
import localization as i18n
from localization import tr
from appearance import apply_theme

ROOT = Path(__file__).resolve().parent
GAME = find_game()
GAME_LOG = GAME.parents[2] / 'Saved' / 'Logs' / 'Vein.log'
SAVES = Path(os.environ['LOCALAPPDATA']) / 'Vein' / 'Saved' / 'SaveGames'
SIMPLE = {
    'Heal': '治疗角色', 'RepairItem': '修复手持物品',
    'LearnEveryRecipe': '学习所有配方', 'LearnEveryBuildObject': '学习所有建造',
    'God': '切换无敌', 'FreezeConditions': '切换冻结状态',
    'GiveKey': '给予目标钥匙', 'FillFuel': '加满目标燃料',
    'ListItems': '列出物品 ID', 'DumpConditionsState': '列出角色状态',
}
SIMPLE.update({'HealEveryone':'治疗所有玩家', 'GiveEveryItem':'给予每种物品',
               'Unlock':'解锁准星目标', 'Lockpick':'撬开准星目标',
               'DiscoverEveryLocation':'发现全部地点', 'RemoveAllCorpses':'清除全部尸体',
               'RandomizeTime':'随机时间', 'ClearWeather':'恢复自然天气'})
WEATHER = {'晴天':'clear', '下雨':'rain', '暴风雪':'blizzard'}


def filter_items(query='', category='全部物品'):
    words = query.strip().casefold().split()
    return [item for item in ITEMS
            if (category == '全部物品' or item['category'] == category)
            and all(word in (' '.join((item['name'], item['id'], item['original']))).casefold()
                    for word in words)]


class ItemPicker:
    def __init__(self, app):
        self.app = app
        app.pickers.append(self)
        self.window = tk.Toplevel(app.root)
        self.window.title('中文物品库 · 选择物品后直接添加')
        self.window.geometry('980x700')
        self.window.minsize(800, 570)
        self.window.configure(bg='#141a20')
        body = ttk.Frame(self.window, padding=18)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text='中文物品库', font=('Microsoft YaHei UI', 20, 'bold')).pack(anchor='w')
        ttk.Label(body, text=tr('内置 {count} 种真实物品 · 选择分类或输入中文搜索',count=f'{len(ITEMS):,}')).pack(anchor='w', pady=(4, 6))
        ttk.Label(body,text=tr('物品名称沿用游戏中文，支持中文和内部编号搜索。')).pack(anchor='w',pady=(0,12))
        self.query = tk.StringVar()
        search = ttk.Frame(body)
        search.pack(fill='x', pady=(0, 12))
        ttk.Label(search, text='搜索物品  ').pack(side='left')
        entry = ttk.Entry(search, textvariable=self.query)
        entry.pack(side='left', fill='x', expand=True)
        ttk.Button(search, text='清空', command=lambda: self.query.set('')).pack(side='left', padx=(8, 0))
        middle = ttk.Frame(body)
        middle.pack(fill='both', expand=True)
        self.categories = ['全部物品'] + sorted({item['category'] for item in ITEMS})
        self.category_list = tk.Listbox(middle, width=19, exportselection=False, bg='#1e2a35', fg='#e6edf3',
                                       selectbackground='#26775f', selectforeground='white', relief='flat',
                                       font=('Microsoft YaHei UI', 10), activestyle='none')
        self.category_list.pack(side='left', fill='y', padx=(0, 12))
        for category in self.categories:
            self.category_list.insert('end', category)
        self.category_list.selection_set(0)
        results = ttk.Frame(middle)
        results.pack(side='left', fill='both', expand=True)
        self.table = ttk.Treeview(results, columns=('name', 'category'), show='headings', selectmode='browse')
        self.table.heading('name', text='物品名称')
        self.table.heading('category', text='分类')
        self.table.column('name', width=390, minwidth=220)
        self.table.column('category', width=160, minwidth=120)
        self.table.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(results, orient='vertical', command=self.table.yview)
        scrollbar.pack(side='right', fill='y')
        self.table.configure(yscrollcommand=scrollbar.set)
        self.summary = tk.StringVar()
        ttk.Label(body, textvariable=self.summary).pack(anchor='w', pady=(10, 5))
        bottom = ttk.Frame(body)
        bottom.pack(fill='x')
        self.selected = tk.StringVar(value='请先选中一种物品')
        ttk.Label(bottom, textvariable=self.selected).pack(side='left', fill='x', expand=True)
        ttk.Label(bottom, text='数量  ').pack(side='left')
        self.quantity = tk.StringVar(value='1')
        ttk.Spinbox(bottom, from_=1, to=1000, width=8, textvariable=self.quantity).pack(side='left', padx=(0, 12))
        self.add_button = ttk.Button(bottom, text='一键添加', command=self.add, state='disabled')
        self.add_button.pack(side='left')
        self.rows = {}
        self.query.trace_add('write', lambda *_: self.refresh())
        self.category_list.bind('<<ListboxSelect>>', lambda _: self.refresh())
        self.table.bind('<<TreeviewSelect>>', self.select)
        self.table.bind('<Return>', lambda _: self.add())
        self.refresh()
        self.localize()
        entry.focus_set()

    def localize(self):
        i18n.translate_tree(self.window)
        self.category_list.delete(0,'end')
        for category in self.categories:self.category_list.insert('end',tr(category))
        self.category_list.selection_set(0)
        self.refresh()
        apply_theme(self.window,i18n.THEME)

    def refresh(self):
        selection = self.category_list.curselection()
        category = self.categories[selection[0]] if selection else '全部物品'
        items = filter_items(self.query.get(), category)
        self.table.delete(*self.table.get_children())
        self.rows = {item['id']: item for item in items}
        for item in items:
            self.table.insert('', 'end', iid=item['id'], values=(item['name'], tr(item['category'])))
        self.summary.set(tr('找到 {count} 种物品',count=len(items)) if items else tr('没有匹配结果，请更换关键词或分类。'))
        self.selected.set(tr('请先选中一种物品'))
        self.add_button.configure(state='disabled')

    def select(self, _=None):
        selected = self.table.selection()
        if selected and selected[0] in self.rows:
            self.selected.set(tr('已选择：') + self.rows[selected[0]]['name'])
            self.add_button.configure(state='normal')
        else:
            self.add_button.configure(state='disabled')

    def add(self):
        selected = self.table.selection()
        if not selected or selected[0] not in self.rows:
            return
        item = self.rows[selected[0]]
        try:
            command = build_command('GiveItem', item['id'], self.quantity.get())
        except ValueError as error:
            messagebox.showerror(tr('数量需要调整'), tr(str(error)), parent=self.window)
            return
        self.app.execute(command)
        self.app.note(f'所选物品：{item["name"]} × {self.quantity.get()}')


def build_command(name, *args):
    if name in SIMPLE and not args:
        return name
    if name in ('AddTime', 'SpawnHorde') and len(args) == 1:
        value = str(args[0]).strip()
        limit = 86400 if name == 'AddTime' else 255
        if not re.fullmatch(r'-?\d{1,6}', value) or not (-limit if name == 'AddTime' else 1) <= int(value) <= limit:
            raise ValueError(f'请输入范围内的整数（最大 {limit}）。')
        return f'{name} {int(value)}'
    if name in ('SetWeather', 'TeleportTo', 'SetTiresPunctured') and len(args) == 1:
        value = str(args[0])
        allowed = WEATHER.values() if name == 'SetWeather' else ('false',) if name == 'SetTiresPunctured' else [x['id'] for x in LOCATIONS]
        if value not in allowed:
            raise ValueError('请选择列表中的选项。')
        return f'{name} {value}'
    if name not in ('AddXP', 'GiveItem', 'SetCondition') or len(args) != 2:
        raise ValueError('指令或参数数量无效。')
    identifier, value = (str(x).strip() for x in args)
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,95}', identifier):
        raise ValueError('请输入英文内部 ID，只能包含字母、数字和下划线。')
    if not re.fullmatch(r'\d{1,7}(?:\.\d{1,6})?', value):
        raise ValueError('请使用普通非负数字，最多六位小数。')
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise ValueError('请输入有效数值。') from None
    limit = Decimal(1000 if name == 'GiveItem' else 1000000 if name == 'AddXP' else 100)
    if not number.is_finite() or number < (1 if name == 'GiveItem' else 0) or number > limit:
        raise ValueError(f'数值超出范围：{"1" if name == "GiveItem" else "0"}–{limit}。')
    if name == 'GiveItem' and number != number.to_integral_value():
        raise ValueError('物品数量必须是整数。')
    return f'{name} {identifier} {format(number, "f")}'


def command_receipt(text, command):
    if re.search(r'command not recognized|no authority|not authorized|permission denied', text, re.I):
        return 'rejected'
    if re.search(r'Cmd:\s*' + re.escape(command) + r'\s*$', text, re.M | re.I):
        return 'received'
    if command == 'DumpConditionsState' and 'Overall Condition Effects:' in text:
        return 'received'
    if command.startswith('GiveItem ') and re.search(r'Gave ' + re.escape(command.split()[-1]) + r' .+ to ', text):
        return 'received'
    return 'unknown'


def condition_value(option, text):
    if option is None or not re.fullmatch(r'-?\d{1,4}(?:\.\d{1,6})?', text.strip()):
        raise ValueError('请选择状态并输入普通数字。')
    value = float(text)
    if not option['min'] <= value <= option['max']:
        raise ValueError(f'该状态允许范围：{option["min"]:g}–{option["max"]:g}。')
    return value


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def backup_saves(source=SAVES, destination=ROOT / 'backups'):
    files = [p for p in source.glob('*.vns') if p.stem.casefold() != 'start']
    if not files:
        raise ValueError('没有找到可备份的存档（start 已排除）。')
    destination.mkdir(parents=True, exist_ok=True)
    target = Path(tempfile.mkdtemp(prefix=datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=destination))
    manifest = {}
    for path in files:
        before = path.stat()
        copied = target / path.name
        shutil.copy2(path, copied)
        checksum = digest(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or digest(copied) != checksum:
            raise OSError('备份期间存档发生变化，请回到游戏主菜单后重试。未完成的副本保留供检查。')
        manifest[path.name] = checksum
    (target / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return target


user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
kernel32.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
kernel32.OpenProcess.restype = w.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [w.HANDLE, w.DWORD, w.LPWSTR, ctypes.POINTER(w.DWORD)]
kernel32.CloseHandle.argtypes = [w.HANDLE]
user32.GetForegroundWindow.restype = w.HWND
user32.SetForegroundWindow.argtypes = [w.HWND]
user32.IsWindowVisible.argtypes = [w.HWND]
user32.GetWindowThreadProcessId.argtypes = [w.HWND, ctypes.POINTER(w.DWORD)]


def game_windows():
    result = []
    callback_type = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)

    @callback_type
    def visit(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        pid = w.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        handle = kernel32.OpenProcess(0x1000, False, pid.value)
        if handle:
            try:
                size = w.DWORD(32768)
                path = ctypes.create_unicode_buffer(size.value)
                if kernel32.QueryFullProcessImageNameW(handle, 0, path, ctypes.byref(size)):
                    if os.path.normcase(path.value) == os.path.normcase(str(GAME)):
                        result.append(hwnd)
            finally:
                kernel32.CloseHandle(handle)
        return True

    user32.EnumWindows(visit, 0)
    return result


class MouseInput(ctypes.Structure):
    _fields_ = [('dx', w.LONG), ('dy', w.LONG), ('mouseData', w.DWORD), ('dwFlags', w.DWORD),
                ('time', w.DWORD), ('dwExtraInfo', ctypes.c_size_t)]


class KeyInput(ctypes.Structure):
    _fields_ = [('vk', w.WORD), ('scan', w.WORD), ('flags', w.DWORD), ('time', w.DWORD),
                ('extra', ctypes.c_size_t)]


class InputUnion(ctypes.Union):
    _fields_ = [('ki', KeyInput), ('mi', MouseInput)]


class Input(ctypes.Structure):
    _anonymous_ = ('data',)
    _fields_ = [('type', w.DWORD), ('data', InputUnion)]


user32.SendInput.argtypes = [w.UINT, ctypes.POINTER(Input), ctypes.c_int]


def send_to_console(hwnd, command):
    if hwnd not in game_windows():
        raise OSError('游戏窗口已变化，已取消发送。')
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.25)
    if user32.GetForegroundWindow() != hwnd:
        raise OSError('无法激活游戏。请让工具和游戏使用相同权限后重试。')

    def emit(vk=0, scan=0, flags=0):
        if user32.GetForegroundWindow() != hwnd:
            raise OSError('焦点已移走，已中止。请清空游戏控制台中的半条指令。')
        events = (Input * 2)(Input(type=1, ki=KeyInput(vk, scan, flags, 0, 0)),
                             Input(type=1, ki=KeyInput(vk, scan, flags | 2, 0, 0)))
        if user32.SendInput(2, events, ctypes.sizeof(Input)) != 2:
            raise ctypes.WinError(ctypes.get_last_error())

    # shortcut: user confirms gameplay focus; this build uses the default ~ console key.
    emit(vk=0xC0)
    time.sleep(0.25)
    ctrl = Input(type=1, ki=KeyInput(0x11, 0, 0, 0, 0))
    release = Input(type=1, ki=KeyInput(0x11, 0, 2, 0, 0))
    if user32.SendInput(1, ctypes.byref(ctrl), ctypes.sizeof(Input)) != 1:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        emit(vk=0x41)
    finally:
        user32.SendInput(1, ctypes.byref(release), ctypes.sizeof(Input))
    for char in command:
        emit(scan=ord(char), flags=4)
        time.sleep(0.006)
    emit(vk=0x0D)


class App:
    def __init__(self, root):
        from trainer_ui import build_ui
        self.root = root
        self.runtime = None
        self.bridge = None
        self.busy = False
        self.toggles = {}
        self.weather = WEATHER
        self.hotkeys = Hotkeys(ROOT / '快捷键设置.json')
        self.hotkey_dialog = None
        self.pickers = []
        self.notes = []
        i18n.load()
        build_ui(self)
        self.apply_preferences()
        root.update_idletasks()
        self.hotkeys.attach(root.winfo_id())
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.note('准备就绪。快捷键在游戏或修改器位于前台时生效。持续功能开关有不同提示音。')
        for error in self.hotkeys.load(self.actions):
            self.note(error)
        self.update_hotkey_labels()
        self.refresh()
        self.root.after(100, self.maintain)
        self.root.after(50, self.poll_hotkeys)

    def open_items(self):
        ItemPicker(self)

    def apply_preferences(self, persist=False):
        i18n.translate_tree(self.root)
        self.root.title(tr('VEIN修改器'))
        self.play_button.show(self.armed.get())
        self.theme_button.update_label('白天模式' if i18n.THEME=='dark' else '夜间模式')
        for action, combo in self.combos.items():
            index=max(0,combo.current())
            rows=self.fields[action][2]
            labels=[row.get('original',row['name']) if action=='TeleportTo' and i18n.LANG!='zh' else tr(row['name']) for row in rows]
            combo.configure(values=labels)
            combo.current(index)
        self.update_hotkey_labels()
        self.status.set(tr(self.status.get()))
        self.output.delete('1.0','end')
        for stamp,message in self.notes:
            self.output.insert('end',stamp+'  '+tr(message)+'\n')
        self.output.see('end')
        for picker in self.pickers:
            if picker.window.winfo_exists():picker.localize()
        apply_theme(self.root,i18n.THEME)
        if persist:
            try:i18n.save()
            except OSError as error:self.note('无法保存界面设置：'+str(error))

    def change_language(self):
        i18n.LANG=next(key for key,value in i18n.LANGUAGES.items() if value==self.language_choice.get())
        self.apply_preferences(True)

    def change_theme(self):
        i18n.THEME='light' if i18n.THEME=='dark' else 'dark'
        self.apply_preferences(True)

    def open_help(self):
        translated=ROOT / 'docs' / f'help_{i18n.LANG}.txt'
        os.startfile(translated if translated.exists() else ROOT / '使用说明.txt')

    def flip(self, key):
        self.toggles[key].set(not self.toggles[key].get())
        self.toggle(key)

    def start_stop(self):
        if self.busy:
            self.note('请等待上一条操作完成后再点击。')
            return
        if not self.armed.get():
            try:
                self.connected()
                self.armed.set(True)
                self.note('已开始：可点击功能，或切回游戏使用已设置的快捷键。')
                sound('on')
            except OSError as error:
                self.note('无法开始：' + str(error))
                sound('error')
            return
        self.armed.set(False)
        self.toggles['无限耐力'].set(False)
        try:
            if self.bridge:
                self.bridge.close()
                self.bridge=None
            if self.runtime:
                self.runtime.close()
            self.note('已停止：快捷键不再执行，持续功能已关闭并恢复原值。')
            sound('off')
        except OSError as error:
            self.note('停止时未能恢复全部原值，请重启游戏：' + str(error))
            sound('error')
        finally:
            self.runtime=None
            for value in self.toggles.values():
                value.set(False)

    def update_hotkey_labels(self):
        for action, buttons in self.hotkey_buttons.items():
            label = self.hotkeys.bindings.get(action, {}).get('label', '设置快捷键')
            for button in buttons:
                button.update_label(label)

    def configure_hotkey(self, action):
        if self.hotkey_dialog is not None:
            self.hotkey_dialog.lift()
            return
        dialog = tk.Toplevel(self.root)
        self.hotkey_dialog = dialog
        dialog.title(tr('设置快捷键')+' · '+tr(self.actions[action][0]))
        dialog.geometry('460x220')
        dialog.resizable(False, False)
        dialog.configure(bg='#0f1112')
        dialog.transient(self.root)
        message = tk.StringVar(value=tr('请按下要使用的快捷键'))
        tk.Label(dialog, textvariable=message, bg='#0f1112', fg='white',
                 font=('Microsoft YaHei UI', 13, 'bold')).pack(pady=(22, 12))
        tk.Label(dialog, text='支持 F1–F12 或 Ctrl / Alt 加字母、数字。\n按键后点击保存；冲突时会提示，不覆盖其他功能。',
                 bg='#0f1112', fg='#9da3a6').pack()
        pending = [None]
        def capture(event):
            if event.keysym in ('Control_L','Control_R','Shift_L','Shift_R','Alt_L','Alt_R'):
                return 'break'
            try:
                pending[0] = key_binding(event.keysym, event.state)
                message.set(pending[0]['label'])
            except ValueError as error:
                message.set(tr(str(error)))
            return 'break'
        def close():
            dialog.grab_release()
            dialog.destroy()
            self.hotkey_dialog = None
        def save(clear=False):
            if pending[0] is None and not clear:
                return
            try:
                binding = None if clear else pending[0]
                if self.hotkeys.bindings.get(action) != binding:
                    self.hotkeys.set(action, binding)
                self.hotkeys.save()
                self.update_hotkey_labels()
                self.note(self.actions[action][0] + ('：快捷键已清除。' if clear else '：快捷键已保存。'))
                close()
            except (OSError, ValueError) as error:
                message.set(tr(str(error)))
                sound('error')
        controls = ttk.Frame(dialog)
        controls.pack(pady=20)
        ttk.Button(controls,text='保存',command=save).pack(side='left',padx=6)
        ttk.Button(controls,text='清除绑定',command=lambda:save(True)).pack(side='left',padx=6)
        ttk.Button(controls,text='取消',command=close).pack(side='left',padx=6)
        i18n.translate_tree(dialog)
        apply_theme(dialog,i18n.THEME)
        dialog.bind('<KeyPress>',capture)
        dialog.protocol('WM_DELETE_WINDOW',close)
        dialog.grab_set()
        dialog.focus_force()

    def poll_hotkeys(self):
        for action in self.hotkeys.poll():
            self.handle_hotkey(action)
        self.root.after(50, self.poll_hotkeys)

    def handle_hotkey(self, action):
        if self.hotkey_dialog is not None or action not in self.actions:
            return
        foreground=user32.GetForegroundWindow()
        owner=w.DWORD()
        user32.GetWindowThreadProcessId(foreground,ctypes.byref(owner))
        windows=game_windows()
        if owner.value!=os.getpid() and foreground not in windows:
            return
        if not self.armed.get():
            self.note('请先回到正常游戏画面，再点击顶部“开始修改”。')
            sound('error')
            return
        if self.busy:
            self.note('请等待上一条操作完成后再点击。')
            sound('error')
            return
        try:
            self.actions[action][1]()
        except (OSError,ValueError) as error:
            self.note('操作中止：'+str(error))
            sound('error')

    def connected(self):
        windows = game_windows()
        if len(windows) != 1:
            raise OSError('未找到唯一的游戏窗口。')
        pid = w.DWORD()
        user32.GetWindowThreadProcessId(windows[0], ctypes.byref(pid))
        if self.runtime is not None and self.runtime.pid != pid.value:
            if self.bridge:
                self.bridge.close()
                self.bridge=None
            self.runtime.close()
            self.runtime = None
            for value in self.toggles.values():
                value.set(False)
        if self.runtime is None:
            self.runtime = Runtime(windows[0], GAME)
        self.runtime.player()
        return self.runtime

    def toggle(self, key):
        enabled = self.toggles[key].get()
        if enabled and not self.armed.get():
            self.toggles[key].set(False)
            self.note('请先回到正常游戏画面，再点击顶部“开始修改”。')
            return
        try:
            runtime = self.connected()
            if key == '无限耐力':
                if enabled:
                    runtime.set_condition('C_Exerted', 0.0)
            else:
                runtime.option(key, enabled)
            self.note(key + ('已开启。' if enabled else '已关闭。'))
            sound('on' if enabled else 'off')
        except (OSError, ValueError) as error:
            self.toggles[key].set(False)
            self.note('操作中止：' + str(error))
            sound('error')

    def maintain(self):
        if self.toggles['无限耐力'].get():
            try:
                self.connected().set_condition('C_Exerted', 0.0)
            except (OSError, ValueError) as error:
                self.toggles['无限耐力'].set(False)
                self.note('无限耐力已停止：' + str(error))
                sound('off')
        self.root.after(100, self.maintain)

    def repair(self):
        try:
            runtime = self.connected()
            before = runtime.equipped()
            self.execute('RepairItem', lambda:self.repair_receipt(before))
        except OSError as error:
            self.note(str(error))

    def repair_receipt(self, before):
        try:
            after = self.connected().equipped()
            if after[0] != before[0]:
                self.note('手持物品发生变化，无法核对，请重新修复。')
            elif after[1] <= 0.000001:
                self.note(f'耐久已核验：{100-before[1]:.2f}% → 100%。')
            else:
                self.note(f'修复尚未生效，当前耐久 {100-after[1]:.2f}%。请检查控制台及手持物品。')
        except OSError as error:
            self.note('无法核验耐久：' + str(error))

    def close(self):
        self.hotkeys.close()
        if self.bridge:
            self.bridge.close()
            self.bridge=None
        self.toggles['无限耐力'].set(False)
        if self.runtime:
            try:
                self.runtime.close()
            except OSError as error:
                self.note('恢复原值未完成：' + str(error))
                messagebox.showerror('请检查游戏', '恢复开关原值失败，请重启游戏恢复默认物理状态。')
        self.root.destroy()

    def note(self, message):
        stamp = datetime.now().strftime('%H:%M:%S')
        line = stamp + '  ' + message + '\n'
        self.notes.append((stamp,message))
        self.notes = self.notes[-200:]
        self.output.insert('end', stamp+'  '+tr(message)+'\n')
        self.output.see('end')
        try:
            with (ROOT / '操作记录.log').open('a', encoding='utf-8') as stream:
                stream.write(line)
        except OSError:
            pass

    def refresh(self):
        windows = game_windows()
        self.status.set(tr('已找到 VEIN 游戏窗口' if len(windows) == 1 else '未找到唯一的 VEIN 窗口，请先启动游戏'))
        self.root.after(2500, self.refresh)

    def parameter(self, name):
        try:
            selected, value, options = self.fields[name]
            index=self.combos[name].current() if name in self.combos else -1
            option=options[index] if 0<=index<len(options) else None
            if name == 'SetCondition':
                if not self.armed.get():
                    raise ValueError('请先回到正常游戏画面，再点击顶部“开始修改”。')
                number = condition_value(option, value.get())
                if self.connected().set_condition(option['id'], number):
                    self.note(f'已设置{option["name"]}：{number:g}，数据回读已核验。')
                    sound('done')
                elif number != 0:
                    self.execute(f'SetCondition {option["id"]} {number:g}')
                else:
                    self.note('角色没有该状态，无需清除。')
            elif name == 'AddXP':
                self.execute(build_command(name, option['id'], value.get()))
            elif name in ('SetWeather', 'TeleportTo'):
                self.execute(build_command(name, option['id']))
            else:
                self.execute(build_command(name, value.get()))
        except (OSError, ValueError) as error:
            messagebox.showerror(tr('参数需要调整'), tr(str(error)))

    def execute(self, command, callback=None):
        if self.busy:
            self.note('请等待上一条操作完成后再点击。')
            return
        if not self.armed.get():
            self.note('尚未发送：请回到正常游戏画面，再点击顶部“开始修改”。')
            return
        windows = game_windows()
        if len(windows) != 1:
            self.note('尚未发送：未找到唯一的游戏窗口。')
            return
        try:
            runtime=self.connected()
            self.busy = True
            label = SIMPLE.get(command, {'GiveItem':'添加所选物品','AddXP':'增加经验','SetWeather':'设置天气',
                                         'TeleportTo':'传送','SpawnHorde':'生成尸潮','AddTime':'增加时间',
                                         'SetCondition':'设置状态','SetTiresPunctured':'修复轮胎'}.get(command.split()[0], '操作'))
            if command.split()[0] in DIRECT_COMMANDS:
                if self.bridge is None:
                    self.bridge=Bridge(runtime,windows[0])
                self.bridge.submit(command)
                self.note('正在执行：'+label+'。')
                self.root.after(25,lambda:self.native_receipt(callback))
                return
            if command.split()[0] not in ('GiveItem','GiveEveryItem'):
                raise ValueError('不支持的直接操作。')
            offset = GAME_LOG.stat().st_size if GAME_LOG.exists() else 0
            send_to_console(windows[0], command)
            self.note('已发送：' + label + '。等待游戏回执。')
            sound('done')
            self.root.after(1100, lambda: self.receipt(command, offset, callback))
        except (OSError,ValueError) as error:
            self.busy = False
            self.note('发送中止：' + str(error))
            sound('error')

    def native_receipt(self,callback):
        try:
            if not self.bridge:
                raise OSError('游戏连接已关闭。')
            if not self.bridge.poll():
                self.root.after(25,lambda:self.native_receipt(callback))
                return
            self.busy=False
            self.note('游戏已接受操作。请核对效果。')
            sound('done')
            if callback:
                self.root.after(150,callback)
        except OSError as error:
            self.busy=False
            self.note('操作中止：'+str(error))
            sound('error')

    def receipt(self, command, offset, callback=None):
        try:
            with GAME_LOG.open('rb') as stream:
                stream.seek(offset)
                text = stream.read(256 * 1024).decode('utf-8', errors='replace')
            state = command_receipt(text, command)
            self.note({'received': '游戏日志已记录指令；请在游戏中核对效果。',
                       'rejected': '游戏返回拒绝或未知指令，请检查权限及参数。',
                       'unknown': '未获得明确日志回执，请查看游戏控制台；不要直接重复切换类功能。'}[state])
        except OSError:
            self.note('无法读取游戏回执，请在游戏中核对效果。')
        finally:
            self.busy = False
        if callback:
            callback()

    def backup(self):
        self.note('开始备份，请保持游戏位于主菜单，避免自动保存。')
        self.root.update_idletasks()
        try:
            target = backup_saves()
            self.note('备份校验完成：' + str(target))
        except (OSError, ValueError) as error:
            self.note('备份未完成：' + str(error))


if __name__ == '__main__':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ctypes.c_wchar_p('VEIN.Trainer'))
    except OSError:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (OSError, AttributeError):
        pass
    window = tk.Tk()
    window.iconbitmap(str(ROOT / 'vein.ico'))
    App(window)
    window.mainloop()
