import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vein_helper as helper
import hotkeys
from runtime_state import Runtime
from unittest.mock import patch


class HelperTests(unittest.TestCase):
    def test_stamina_only_resets_exertion_and_rechecks_array(self):
        class Fake(Runtime):
            def __init__(self):self.writes=[];self.changed=False
            def conditions(self):return 1000,2000,{'C_Exerted':(3000,40),'C_Thirst':(3064,20)}
            def pointer(self,address):return 9999 if self.changed else 2000
            def name(self,index):return 'C_Exerted'
            def unpack(self,address,fmt):return 0
            def write(self,address,data):self.writes.append((address,data))
        import struct
        runtime=Fake()
        self.assertTrue(runtime.set_condition('C_Exerted',0.0))
        self.assertEqual(runtime.writes,[(3024,struct.pack('<d',0.0)),(1864,b'\x01')])
        runtime.writes.clear();runtime.changed=True
        with self.assertRaises(OSError):runtime.set_condition('C_Exerted',0.0)
        self.assertEqual(runtime.writes,[])
        self.assertFalse(runtime.set_condition('C_Missing',0.0))

    def test_option_catalogs_and_parameters(self):
        for rows in (helper.STATS, helper.CONDITIONS, helper.LOCATIONS):
            self.assertEqual(len({r['id'] for r in rows}), len(rows))
            for row in rows:
                self.assertTrue(row['name'].isprintable())
                self.assertRegex(row['name'],r'[\u4e00-\u9fff]')
        for row in helper.LOCATIONS:
            helper.build_command('TeleportTo',row['id'])
        for row in helper.CONDITIONS:
            self.assertEqual(helper.condition_value(row,str(row['min'])),row['min'])
            with self.assertRaises(ValueError):helper.condition_value(row,str(row['max']+1))
        self.assertEqual(helper.build_command('AddTime','-3600'),'AddTime -3600')
        self.assertEqual(helper.build_command('SpawnHorde','5'),'SpawnHorde 5')
        for cmd,arg in [('SpawnHorde','256'),('SpawnHorde','0'),('AddTime','1;Quit'),('SetWeather','bogus'),('TeleportTo','unknown')]:
            with self.assertRaises(ValueError):helper.build_command(cmd,arg)

    def test_hotkey_validation_conflicts_and_persistence(self):
        binding=hotkeys.key_binding('F8',4)
        self.assertEqual(binding,{'modifiers':2,'vk':0x77,'label':'Ctrl+F8'})
        self.assertEqual(hotkeys.key_binding('k',0x20004)['label'],'Ctrl+Alt+K')
        for key,state in [('a',0),('a',1),('Return',0),('F13',0)]:
            with self.assertRaises(ValueError):hotkeys.key_binding(key,state)
        with tempfile.TemporaryDirectory() as folder, patch.object(hotkeys,'u') as api:
            api.RegisterHotKey.return_value=True
            manager=hotkeys.Hotkeys(Path(folder)/'keys.json')
            manager.set('test',binding)
            with self.assertRaises(ValueError):manager.set('other',binding)
            api.RegisterHotKey.return_value=False
            with self.assertRaises(OSError):manager.set('test',hotkeys.key_binding('F9',4))
            self.assertEqual(manager.bindings['test'],binding)
            manager.save();manager.close()
            api.RegisterHotKey.return_value=True
            second=hotkeys.Hotkeys(manager.path)
            self.assertEqual(second.load({'test':('测试',lambda:None)}),[])
            self.assertEqual(second.bindings['test'],binding)
            second.set('test',None);second.close()

    def test_chinese_catalog_search_and_categories(self):
        self.assertEqual(len(helper.ITEMS), 1362)
        self.assertEqual(len({item['id'] for item in helper.ITEMS}), len(helper.ITEMS))
        for item in helper.ITEMS:
            self.assertRegex(item['name'], r'[\u4e00-\u9fff]')
            helper.build_command('GiveItem', item['id'], '1')
        found = helper.filter_items('酵母', '全部物品')
        self.assertTrue(any(item['id'] == 'BP_YeastBag' for item in found))
        self.assertTrue(all(item['category'] == '服装与护具' for item in helper.filter_items('', '服装与护具')))
        self.assertEqual(helper.filter_items('不会存在的物品名称123', '全部物品'), [])
        self.assertEqual(helper.filter_items('酵母', '服装与护具'), [])
        self.assertEqual(helper.filter_items('bp_yeastbag', '全部物品')[0]['id'], 'BP_YeastBag')

    def test_commands_and_boundaries(self):
        self.assertEqual(helper.build_command('Heal'), 'Heal')
        self.assertEqual(helper.build_command('AddXP', 'Strength', '250'), 'AddXP Strength 250')
        self.assertEqual(helper.build_command('GiveItem', 'Apple', '2'), 'GiveItem Apple 2')
        self.assertEqual(helper.build_command('SetCondition', 'Hunger', '0.5'), 'SetCondition Hunger 0.5')
        for command, args in [('Quit', ()), ('Heal', ('x',)), ('GiveItem', ('Apple;Quit', '2')),
                              ('GiveItem', ('Apple', '0')), ('GiveItem', ('Apple', '1.2')),
                              ('AddXP', ('Strength', 'nan')), ('AddXP', ('Strength', '1000001')),
                              ('AddXP', ('Strength', '1e-99999999')),
                              ('SetCondition', ('Hunger\nQuit', '1'))]:
            with self.subTest(command=command, args=args), self.assertRaises(ValueError):
                helper.build_command(command, *args)

    def test_log_receipt_is_not_effect_confirmation(self):
        self.assertEqual(helper.command_receipt('LogTemp: other', 'Heal'), 'unknown')
        self.assertEqual(helper.command_receipt('LogConsoleResponse: Command not recognized: Heal', 'Heal'), 'rejected')
        self.assertEqual(helper.command_receipt('LogConsoleResponse: No authority', 'Heal'), 'rejected')
        self.assertEqual(helper.command_receipt('LogConsoleResponse: Cmd: Heal', 'Heal'), 'received')
        self.assertEqual(helper.command_receipt('Cmd: HealEveryone', 'Heal'), 'unknown')
        self.assertEqual(helper.command_receipt('LogVein: Overall Condition Effects:', 'DumpConditionsState'), 'received')
        self.assertEqual(helper.command_receipt('LogVein: Gave 1 item to Player', 'GiveItem BP_YeastBag 1'), 'received')

    def test_backup_excludes_start_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'saves'
            source.mkdir()
            (source / 'start.vns').write_bytes(b'do not use')
            (source / 'Test.vns').write_bytes(b'VEINSAVE test')
            target = helper.backup_saves(source, root / 'backups')
            self.assertEqual((target / 'Test.vns').read_bytes(), b'VEINSAVE test')
            self.assertFalse((target / 'start.vns').exists())
            self.assertTrue((target / 'manifest.json').is_file())
            self.assertNotEqual(target, helper.backup_saves(source, root / 'backups'))


if __name__ == '__main__':
    unittest.main()
