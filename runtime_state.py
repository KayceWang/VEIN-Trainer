"""当前已核对版本的单机数据访问；不注入代码，不修改游戏文件。"""
import ctypes as c
from ctypes import wintypes as w
import hashlib
import math
import struct

SUPPORTED_HASH = '97707445b6e3b940c9efddca605124aac64d577f2945019efaa98122818344d5'
k = c.WinDLL('kernel32', use_last_error=True)
k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
k.OpenProcess.restype = w.HANDLE
k.CloseHandle.argtypes = [w.HANDLE]
k.ReadProcessMemory.argtypes = [w.HANDLE, c.c_void_p, c.c_void_p, c.c_size_t, c.POINTER(c.c_size_t)]
k.WriteProcessMemory.argtypes = k.ReadProcessMemory.argtypes
ps = c.WinDLL('psapi')
ps.EnumProcessModules.argtypes = [w.HANDLE, c.c_void_p, w.DWORD, c.POINTER(w.DWORD)]


class Runtime:
    def __init__(self, hwnd, game):
        with game.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != SUPPORTED_HASH:
                raise OSError('游戏版本变化，已停止数据修改。请重新适配。')
        pid = w.DWORD()
        c.windll.user32.GetWindowThreadProcessId(hwnd, c.byref(pid))
        self.pid = pid.value
        self.handle = k.OpenProcess(0x438, False, self.pid)
        if not self.handle:
            raise c.WinError(c.get_last_error())
        self.restores = {}
        try:
            modules = (c.c_void_p * 1024)()
            size = w.DWORD()
            if not ps.EnumProcessModules(self.handle, modules, c.sizeof(modules), c.byref(size)):
                raise c.WinError(c.get_last_error())
            self.base = modules[0]
            # Also check the loaded image, in case the file changed after launch.
            pe = struct.unpack('<I', self.read(self.base + 60, 4))[0]
            with game.open('rb') as stream:
                stream.seek(pe)
                expected = stream.read(24)
            if self.read(self.base + pe, 24) != expected:
                raise OSError('运行中的游戏与磁盘版本不一致。')
            self.player()
        except Exception:
            self.close()
            raise

    def read(self, address, size):
        if not 0x10000 < address < 0x7fffffffffff or not 0 < size <= 1024 * 1024:
            raise OSError('游戏数据地址无效。')
        buffer = c.create_string_buffer(size)
        count = c.c_size_t()
        if not k.ReadProcessMemory(self.handle, address, buffer, size, c.byref(count)) or count.value != size:
            raise OSError('游戏数据已变化，请重新连接。')
        return buffer.raw

    def unpack(self, address, fmt):
        return struct.unpack(fmt, self.read(address, struct.calcsize(fmt)))[0]

    def pointer(self, address):
        return self.unpack(address, '<Q')

    def name(self, index):
        block = self.pointer(self.base + 0xaf60c80 + 16 + (index >> 16) * 8)
        entry = block + (index & 65535) * 2
        header = self.unpack(entry, '<H')
        length = header >> 6
        if not 0 < length < 1024:
            raise OSError('游戏名称表不匹配。')
        return self.read(entry + 2, length * (2 if header & 1 else 1)).decode('utf-16-le' if header & 1 else 'utf-8')

    def object_name(self, obj):
        return self.name(self.unpack(obj + 24, '<I'))

    def player(self):
        world = self.pointer(self.base + 0xb2186b8)
        if self.pointer(world + 56):
            raise OSError('数据修改仅支持本机单机世界，请退出联机。')
        gi = self.pointer(world + 552)
        if self.unpack(gi + 64, '<i') != 1:
            raise OSError('未找到唯一的本地玩家。')
        lp = self.pointer(self.pointer(gi + 56))
        controller = self.pointer(lp + 48)
        pawn = self.pointer(controller + 768)
        if self.object_name(pawn) != 'BP_VeinPlayerCharacter_C':
            raise OSError('角色尚未进入可操作世界。')
        return pawn

    def write(self, address, data):
        self.player()
        count = c.c_size_t()
        if not k.WriteProcessMemory(self.handle, address, data, len(data), c.byref(count)) or count.value != len(data):
            raise OSError('写入未完成，请关闭功能并重新连接。')
        if self.read(address, len(data)) != data:
            raise OSError('数据回读不一致，功能已中止。')

    def conditions(self):
        component = self.pointer(self.player() + 2720)
        array = self.pointer(component + 568)
        count = self.unpack(component + 576, '<i')
        if not 0 <= count <= 256:
            raise OSError('角色状态列表异常。')
        result = {}
        for i in range(count):
            address = array + i * 64
            key = self.name(self.unpack(address + 12, '<I'))
            value = self.unpack(address + 24, '<d')
            if not math.isfinite(value):
                raise OSError('角色状态数值异常。')
            result[key] = (address, value)
        return component, array, result

    def set_condition(self, key, value):
        component, array, rows = self.conditions()
        if key not in rows:
            return False
        address, _ = rows[key]
        # Recheck the array and identity immediately before writing.
        if self.pointer(component + 568) != array or self.name(self.unpack(address + 12, '<I')) != key:
            raise OSError('状态列表发生变化，请重试。')
        self.write(address + 24, struct.pack('<d', value))
        self.write(component + 864, b'\x01')
        return True

    def option(self, key, enabled):
        pawn = self.player()
        if key == '无敌模式':
            address=pawn+0x62
            raw=self.read(address,1)
            if enabled:
                if key not in self.restores:self.restores[key]=(pawn,pawn,address,bytes([raw[0]&4]))
                self.write(address,bytes([raw[0]&~4]))
            elif key in self.restores:
                oldpawn,owner,oldaddress,original=self.restores[key]
                if oldpawn==pawn and oldaddress==address:
                    self.write(address,bytes([(raw[0]&~4)|original[0]]))
                del self.restores[key]
            return
        if key == '低重力':
            owner = self.pointer(pawn + 840)
            address, fmt, value = owner + 424, '<f', 0.3
        elif key == '超级速度':
            owner, address, fmt, value = pawn, pawn + 4064, '<f', 5.0
        elif key == '超级跳跃':
            owner, address, fmt, value = pawn, pawn + 4060, '<?', True
        else:
            raise ValueError('未知功能。')
        if enabled:
            if key not in self.restores:
                original = self.read(address, struct.calcsize(fmt))
                self.restores[key] = (pawn, owner, address, original)
            self.write(address, struct.pack(fmt, value))
        elif key in self.restores:
            oldpawn, oldowner, oldaddress, original = self.restores[key]
            if oldpawn == pawn and oldaddress == address and oldowner == owner:
                self.write(address, original)
            del self.restores[key]

    def equipped(self):
        pawn = self.player()
        equipped = pawn + 2880
        item_id = self.read(equipped + 104, 4)
        if item_id == b'\xff' * 4 or not self.pointer(equipped):
            raise OSError('请先把需要修复的武器或工具拿在手里，再关闭背包。')
        inventory = self.pointer(pawn + 2712)
        array = self.pointer(inventory + 504)
        count = self.unpack(inventory + 512, '<i')
        if not 0 <= count <= 10000:
            raise OSError('背包数据异常。')
        for i in range(count):
            address = array + i * 168
            if self.read(address + 104, 4) == item_id:
                damage = self.unpack(address + 96, '<d')
                if not 0 <= damage <= 100:
                    raise OSError('物品耐久数值异常。')
                return item_id, damage
        raise OSError('未找到手持物品的背包实例，请重新装备。')

    def close(self):
        if getattr(self, 'handle', None):
            try:
                for key in list(self.restores):
                    self.option(key, False)
            finally:
                k.CloseHandle(self.handle)
                self.handle = None
