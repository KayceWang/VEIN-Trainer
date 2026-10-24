import sys,tempfile,json
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import vein_helper as h
import localization as l
from trainer_ui import Switch
def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)
with tempfile.TemporaryDirectory() as folder,patch.object(l,'SETTINGS',Path(folder)/'ui.json'):
    root=tk.Tk();root.withdraw();app=h.App(root)
    try:
        app.toggles['无限耐力'].set(True)
        app.armed.set(True)
        for code,label in l.LANGUAGES.items():
            app.language_choice.set(label);app.change_language()
            for mode in ('light','dark'):
                if l.THEME!=mode:app.change_theme()
                root.update_idletasks()
                assert root.title()==l.tr('VEIN修改器')
                assert root.cget('bg')==('#f0f2f5' if mode=='light' else '#0b0d0e')
                assert app.armed.get() and app.toggles['无限耐力'].get()
                assert app.combos['AddXP'].current()==0
                assert app.combos['SetCondition'].current()==0
                assert json.loads(l.SETTINGS.read_text(encoding='utf-8'))=={'language':code,'theme':mode}
                for widget in descendants(root):
                    if isinstance(widget,Switch):
                        assert widget.itemcget(widget.action_label,'text') in (l.tr('开启'),l.tr('关闭'))
                    if isinstance(widget,tk.Canvas) and hasattr(widget,'_text_sources'):
                        for item,source in widget._text_sources.items():
                            assert widget.itemcget(item,'text')==l.tr(source),(code,source,widget.itemcget(item,'text'))
                    if isinstance(widget,tk.Label) and hasattr(widget,'_source_text'):
                        assert widget.cget('text')==l.tr(widget._source_text)
                if code!='zh':
                    for rows in (h.STATS,h.CONDITIONS):
                        assert all(not any('\u4e00'<=ch<='\u9fff' for ch in l.tr(row['name'])) for row in rows)
        print('5 languages × 2 themes; persistence; active state preserved; translated stat/condition menus: PASS')
    finally:
        app.toggles['无限耐力'].set(False);app.close()
        l.LANG='zh';l.THEME='dark'
