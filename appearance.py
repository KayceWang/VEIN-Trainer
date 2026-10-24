"""对现有控件换色，保留功能开关与快捷键状态。"""
import tkinter as tk
from tkinter import ttk

LIGHT = {
    '#00a2be':'#007f95',
    '#0b0d0e':'#f0f2f5', '#0f1112':'#ffffff', '#1c1e20':'#e7ebef', '#c7c9ca':'#323940',
    '#3c4043':'#d2d8de', '#34383c':'#c7cfd6', '#8a9094':'#7c8790', '#7c8387':'#5e6872',
    '#7e8386':'#65717b', '#8d9498':'#626d76', '#55c5ac':'#08745b', '#5bdaef':'#00758a',
    '#141a20':'#f4f6f8', '#1e2a35':'#e9edf2', '#e6edf3':'#242c34', '#0c1117':'#f8fafc',
    '#d5e0e9':'#35414c', '#9da3a6':'#61717b', '#f6f7f8':'#f9fafb',
}
REVERSE = {value:key for key,value in LIGHT.items()}


def apply_theme(root, mode):
    def color(value):
        base = REVERSE.get(value.lower(), value.lower())
        return LIGHT.get(base,base) if mode=='light' else base
    def walk(widget):
        keys=widget.keys()
        if isinstance(widget,tk.Label) and not hasattr(widget,'_white_on_panel'):
            widget._white_on_panel = str(widget.cget('fg'))=='white' and REVERSE.get(str(widget.cget('bg')),str(widget.cget('bg'))) in ('#0b0d0e','#0f1112')
        for key in ('bg','fg','insertbackground','selectbackground','selectforeground','highlightbackground'):
            if key in keys:
                try:widget.configure(**{key:color(str(widget.cget(key)))})
                except tk.TclError:pass
        if getattr(widget,'_white_on_panel',False):
            widget.configure(fg='#20252a' if mode=='light' else 'white')
        if isinstance(widget,tk.Canvas):
            for item in widget.find_all():
                for key in ('fill','outline'):
                    try:
                        value=widget.itemcget(item,key)
                        if value:widget.itemconfigure(item,**{key:color(value)})
                    except tk.TclError:pass
            if hasattr(widget,'color') and hasattr(widget,'shape') and hasattr(widget,'label'):
                widget.color=color(widget.color)
                widget.itemconfigure(widget.shape,fill=widget.color)
                accent=color('#00a2be')
                widget.itemconfigure(widget.label,fill='white' if mode=='dark' or widget.color==accent else '#26323b')
            if hasattr(widget,'action_shape') and hasattr(widget,'action_label'):
                active=widget.itemcget(widget.action_shape,'fill')==color('#1c1e20')
                widget.itemconfigure(widget.action_label,fill='#26323b' if mode=='light' and active else 'white')
        for child in widget.winfo_children():walk(child)
    walk(root)
    bg,field,fg,card=[color(x) for x in ('#0b0d0e','#1c1e20','#c7c9ca','#0f1112')]
    style=ttk.Style(root)
    style.configure('.',background=bg,foreground=fg)
    style.configure('TFrame',background=bg)
    style.configure('TLabel',background=bg,foreground=fg)
    style.configure('TButton',background=field,foreground=fg)
    for name in ('TCombobox','TEntry','TSpinbox'):
        style.configure(name,fieldbackground=field,background=field,foreground=fg,arrowcolor=fg,
                        bordercolor=field,lightcolor=field,darkcolor=field,insertcolor=fg)
        style.map(name,fieldbackground=[('readonly',field)],foreground=[('readonly',fg)])
    style.configure('Treeview',background=card,fieldbackground=card,foreground=fg)
    style.configure('Treeview.Heading',background=field,foreground=fg)
    root.option_add('*TCombobox*Listbox.background',field)
    root.option_add('*TCombobox*Listbox.foreground',fg)
    import trainer_ui
    trainer_ui.BG,trainer_ui.FIELD,trainer_ui.FG,trainer_ui.CARD=bg,field,fg,card
    trainer_ui.CYAN=color('#00a2be')
