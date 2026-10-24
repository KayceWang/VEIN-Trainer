"""与参考图一致的深色、双栏、圆角单页面板。"""
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from localization import tr, LANGUAGES
import localization
from items_catalog import ITEMS
from game_options import STATS, CONDITIONS, LOCATIONS

BG = '#0b0d0e'
CARD = '#0f1112'
FIELD = '#1c1e20'
FG = '#c7c9ca'
CYAN = '#00a2be'


def rounded(canvas, x, y, width, height, radius, color):
    return canvas.create_polygon(x+radius,y, x+width-radius,y, x+width,y,
                                 x+width,y+radius, x+width,y+height-radius,
                                 x+width,y+height, x+width-radius,y+height,
                                 x+radius,y+height, x,y+height, x,y+height-radius,
                                 x,y+radius, x,y, smooth=True, fill=color, outline='')


class Button(tk.Canvas):
    def __init__(self, parent, text, command, width=70, color=CYAN):
        super().__init__(parent, width=width, height=30, bg=parent.cget('bg'),
                         highlightthickness=0, bd=0, takefocus=True, cursor='hand2')
        self.command, self.color = command, color
        self.shape = rounded(self, 0, 0, width, 30, 10, color)
        self.label = self.create_text(width/2, 15, text=tr(text), fill='white', font=('Microsoft YaHei UI', 9, 'bold'))
        self._text_sources={self.label:text}
        self.fit_text()
        self.bind('<Button-1>', lambda _: self.command())
        self.bind('<Return>', lambda _: self.command())
        self.bind('<space>', lambda _: self.command())
        self.bind('<Enter>', lambda _: self.itemconfigure(self.shape, fill='#087f96' if self.color == CYAN else '#303437'))
        self.bind('<Leave>', lambda _: self.itemconfigure(self.shape, fill=self.color))
        self.bind('<FocusIn>', lambda _: self.itemconfigure(self.shape, outline='#75d8e9', width=1))
        self.bind('<FocusOut>', lambda _: self.itemconfigure(self.shape, outline=''))

    def update_label(self, text, active=False):
        self.color = CYAN if active else FIELD
        self.itemconfigure(self.shape, fill=self.color)
        self.itemconfigure(self.label, text=tr(text))
        self._text_sources[self.label]=text
        self.fit_text()

    def fit_text(self):
        width=max(int(self.cget('width')),Font(font=self.itemcget(self.label,'font')).measure(self.itemcget(self.label,'text'))+18)
        self.configure(width=width)
        self.coords(self.label,width/2,15)
        self.delete(self.shape)
        self.shape=rounded(self,0,0,width,30,10,self.color)
        self.tag_lower(self.shape)


class PlayButton(tk.Canvas):
    def __init__(self, parent, command, text='▶  开始修改', color='#f6f7f8', foreground='#343a40'):
        super().__init__(parent,width=190,height=48,bg=BG,highlightthickness=0,cursor='hand2',takefocus=True)
        rounded(self,0,0,190,48,24,color)
        self.label=self.create_text(95,24,text=tr(text),fill=foreground,font=('Microsoft YaHei UI',13,'bold'))
        self._text_sources={self.label:text}
        self.bind('<Button-1>',lambda _:command())
        self.bind('<Return>',lambda _:command())
        self.bind('<space>',lambda _:command())

    def show(self,active):
        source='正在运行   ×' if active else '▶  开始修改'
        self._text_sources[self.label]=source
        self.itemconfigure(self.label,text=tr(source))


class Switch(tk.Canvas):
    def __init__(self,parent,variable,command):
        super().__init__(parent,width=210,height=32,bg=CARD,highlightthickness=0,cursor='hand2',takefocus=True)
        self.rail=rounded(self,0,7,42,18,9,'#34383c')
        self.knob=self.create_oval(3,10,15,22,fill='#8a9094',outline='')
        self.state_label=self.create_text(90,16,text='',fill='#7c8387',font=('Microsoft YaHei UI',9))
        self.action_shape=rounded(self,140,1,70,30,9,FIELD)
        self.action_label=self.create_text(175,16,text=tr('开启'),fill='white',font=('Microsoft YaHei UI',9,'bold'))
        self._text_sources={}
        def render(*_):
            active=variable.get()
            self.itemconfigure(self.rail,fill=CYAN if active else '#34383c')
            self.coords(self.knob,27 if active else 3,10,39 if active else 15,22)
            self.itemconfigure(self.knob,fill='white' if active else '#8a9094')
            self.itemconfigure(self.state_label,text=tr('已开启' if active else '已关闭'),fill=('#00758a' if localization.THEME=='light' else '#5bdaef') if active else '#7c8387')
            self.itemconfigure(self.action_shape,fill=FIELD if active else CYAN)
            self.itemconfigure(self.action_label,text=tr('关闭' if active else '开启'))
            self.itemconfigure(self.action_label,fill='#26323b' if localization.THEME=='light' and active else 'white')
            self._text_sources[self.state_label]='已开启' if active else '已关闭'
            self._text_sources[self.action_label]='关闭' if active else '开启'
        variable.trace_add('write',render)
        render()
        self.bind('<Button-1>',lambda _:command())
        self.bind('<Return>',lambda _:command())
        self.bind('<space>',lambda _:command())


def build_ui(app):
    root = app.root
    root.title('VEIN修改器')
    root.geometry('1360x1040')
    root.minsize(1120, 780)
    root.configure(bg=BG)
    root.option_add('*TCombobox*Listbox.background', FIELD)
    root.option_add('*TCombobox*Listbox.foreground', FG)
    root.option_add('*TCombobox*Listbox.selectBackground', CYAN)
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', font=('Microsoft YaHei UI', 10), background=BG, foreground=FG)
    style.configure('TFrame', background=BG)
    style.configure('TButton', background=FIELD, padding=(10,7), borderwidth=0)
    style.map('TButton', background=[('active','#303437')])
    for name in ('TCombobox','TEntry','TSpinbox'):
        style.configure(name, fieldbackground=FIELD, background=FIELD, foreground=FG,
                        arrowcolor=FG, bordercolor=FIELD, lightcolor=FIELD, darkcolor=FIELD,
                        borderwidth=0, padding=5, insertcolor='white')
        style.map(name, fieldbackground=[('readonly',FIELD)], foreground=[('readonly',FG)])
    style.configure('TCheckbutton', background=BG, foreground=FG)
    style.map('TCheckbutton', background=[('active',BG)], foreground=[('active','white')])
    style.configure('Treeview', background=CARD, fieldbackground=CARD, foreground=FG, rowheight=30)
    style.configure('Treeview.Heading', background=FIELD, foreground=FG)
    style.map('Treeview', background=[('selected','#176275')], foreground=[('selected','white')])
    header = tk.Frame(root, bg=BG)
    header.pack(fill='x', padx=24, pady=(18,8))
    tk.Label(header, text='VEIN修改器', bg=BG, fg='white', font=('Microsoft YaHei UI',15,'bold')).pack(side='left',padx=(0,24))
    tk.Label(header,text='语言：',bg=BG,fg=FG,font=('Microsoft YaHei UI',10)).pack(side='left')
    app.language_choice=tk.StringVar(value=LANGUAGES[localization.LANG])
    language=ttk.Combobox(header,textvariable=app.language_choice,values=list(LANGUAGES.values()),state='readonly',width=13)
    language.pack(side='left',padx=8)
    language.bind('<<ComboboxSelected>>',lambda _:app.change_language())
    app.theme_button=Button(header,'白天模式' if localization.THEME=='dark' else '夜间模式',app.change_theme,width=110,color=FIELD)
    app.theme_button.pack(side='left',padx=8)
    app.status = tk.StringVar(value='正在检查游戏…')
    tk.Label(header, textvariable=app.status, bg=BG, fg='#55c5ac',font=('Microsoft YaHei UI',9)).pack(side='right',padx=20)
    app.armed = tk.BooleanVar(value=False)
    app.play_button=PlayButton(header,app.start_stop)
    app.play_button.pack(side='right',padx=(0,18))
    tk.Label(header,text='请先进入游戏世界',bg=BG,fg='#8d9498',font=('Microsoft YaHei UI',9)).pack(side='right',padx=(12,12))
    app.armed.trace_add('write',lambda *_:app.play_button.show(app.armed.get()))
    nav = tk.Frame(root, bg=BG)
    nav.pack(fill='x',padx=24,pady=(8,12))
    for label in ('▦  全部', '♙  辅助', '⚡  便捷', '◉  优化', '▣  沙盒', '♨  挑战'):
        Button(nav,label,lambda:None,width=100,color='#3c4043' if '全部' in label else FIELD).pack(side='left',padx=(0,3))
    PlayButton(nav,app.open_items,text='▦  刷取物品',color=CYAN,foreground='white').pack(side='right')
    footer = tk.Frame(root,bg=BG)
    footer.pack(side='bottom',fill='x',padx=24,pady=(8,12))
    app.output = tk.Text(footer,height=3,wrap='word',bg=BG,fg='#8d9498',relief='flat',font=('Microsoft YaHei UI',9))
    app.output.pack(side='left',fill='x',expand=True)
    Button(footer,'备份存档',app.backup,width=90,color=FIELD).pack(side='right',padx=5)
    Button(footer,'使用说明',app.open_help,width=90,color=FIELD).pack(side='right',padx=5)
    body = tk.Frame(root,bg=BG)
    body.pack(fill='both',expand=True,padx=20)
    scroll = ttk.Scrollbar(body,orient='vertical')
    scroll.pack(side='right',fill='y')
    canvas = tk.Canvas(body,bg=BG,highlightthickness=0,yscrollcommand=scroll.set)
    canvas.pack(side='left',fill='both',expand=True)
    scroll.configure(command=canvas.yview)
    page = tk.Frame(canvas,bg=BG)
    window = canvas.create_window(0,0,window=page,anchor='nw')
    canvas.bind('<Configure>',lambda event:canvas.itemconfigure(window,width=event.width))
    page.bind('<Configure>',lambda _:canvas.configure(scrollregion=canvas.bbox('all')))
    def wheel(event):
        widget = root.winfo_containing(event.x_root,event.y_root)
        if widget and widget.winfo_toplevel()==root and not isinstance(widget,(ttk.Combobox,ttk.Entry,tk.Text)):
            canvas.yview_scroll(int(-event.delta/120)*3,'units')
    root.bind_all('<MouseWheel>',wheel,add='+')
    app.actions, app.hotkey_buttons, app.fields, app.combos = {}, {}, {}, {}
    sections=[]
    def section(title, symbol):
        outer=tk.Canvas(page,bg=BG,highlightthickness=0,height=100)
        outer.pack(fill='x',pady=(0,14))
        shape=rounded(outer,0,0,100,100,18,CARD)
        tk.Label(outer,text=f'{symbol}   {title}',bg=CARD,fg=FG,font=('Microsoft YaHei UI',10,'bold')).place(x=20,y=12)
        inner=tk.Frame(outer,bg=CARD)
        inner.place(x=22,y=42,relwidth=1,width=-44)
        def resize(_=None):
            height=inner.winfo_reqheight()+52
            outer.configure(height=height)
            outer.coords(shape,20,0, outer.winfo_width()-20,0,outer.winfo_width(),0,
                         outer.winfo_width(),20,outer.winfo_width(),height-20,
                         outer.winfo_width(),height,outer.winfo_width()-20,height,
                         20,height,0,height,0,height-20,0,20,0,0)
        inner.bind('<Configure>',resize)
        outer.bind('<Configure>',resize)
        inner.columnconfigure(0,weight=1,uniform='half')
        inner.columnconfigure(1,weight=1,uniform='half')
        inner.row_count=0
        sections.append((title,outer))
        return inner
    def row(parent,title,action,callback,options=None,default=None,toggle=False):
        i=parent.row_count;parent.row_count+=1
        frame=tk.Frame(parent,bg=CARD,height=54)
        frame.grid(row=i//2,column=i%2,sticky='ew',padx=(0,24) if i%2==0 else (24,0),pady=3)
        frame.pack_propagate(False)
        tk.Label(frame,text=title,bg=CARD,fg=FG,font=('Microsoft YaHei UI',9,'bold'),anchor='w').pack(side='left',fill='x',expand=True)
        hot=Button(frame,'设置快捷键',lambda a=action:app.configure_hotkey(a),width=96,color=FIELD)
        hot.pack(side='right',padx=(10,0))
        app.hotkey_buttons.setdefault(action,[]).append(hot)
        app.actions[action]=(title,callback)
        if toggle:
            variable=app.toggles.setdefault(title,tk.BooleanVar(value=False))
            control=Switch(frame,variable,callback)
        else:
            control=Button(frame,'应用' if default is None else '✓',callback,width=58 if default is None else 34)
        control.pack(side='right')
        if options is not None:
            value=tk.StringVar(value=default or '')
            selected=tk.StringVar(value=options[0]['name'] if options else '')
            if default is not None:
                ttk.Spinbox(frame,textvariable=value,from_=-86400 if action=='AddTime' else 0,to=1000000,width=6).pack(side='right',padx=6)
            if options:
                combo=ttk.Combobox(frame,textvariable=selected,values=[x['name'] for x in options],state='readonly',width=18)
                combo.pack(side='right',padx=6)
                app.combos[action]=combo
            app.fields[action]=selected,value,options
    pinned=section('常用置顶','◆')
    row(pinned,'恢复手持物品耐久','RepairItem',app.repair)
    row(pinned,'无限耐力','toggle:无限耐力',lambda:app.flip('无限耐力'),toggle=True)
    players=section('玩家','♟')
    for key,label in [('Heal','治疗角色'),('HealEveryone','治疗所有玩家')]:
        row(players,label,key,lambda c=key:app.execute(c))
    row(players,'无敌模式','toggle:无敌模式',lambda:app.flip('无敌模式'),toggle=True)
    inv=section('物品与配方','▦')
    for key,label in [('GiveEveryItem','给予每种物品'),('LearnEveryRecipe','学习所有配方'),('LearnEveryBuildObject','学习所有建造')]:
        row(inv,label,key,lambda c=key:app.execute(c))
    row(inv,'恢复手持物品耐久','RepairItem',app.repair)
    stats=section('属性与状态','▥')
    row(stats,'增加经验','AddXP',lambda:app.parameter('AddXP'),STATS,'100')
    row(stats,'设置状态','SetCondition',lambda:app.parameter('SetCondition'),CONDITIONS,'0')
    cars=section('载具','▣')
    row(cars,'给予车辆钥匙','GiveKey',lambda:app.execute('GiveKey'))
    row(cars,'修复轮胎破损','SetTiresPunctured false',lambda:app.execute('SetTiresPunctured false'))
    game=section('游戏','♜')
    for key,label in [('Unlock','解锁目标'),('Lockpick','撬开目标')]:
        row(game,label,key,lambda c=key:app.execute(c))
    row(game,'设置天气','SetWeather',lambda:app.parameter('SetWeather'),[{'id':v,'name':k} for k,v in app.weather.items()])
    row(game,'发现所有地点','DiscoverEveryLocation',lambda:app.execute('DiscoverEveryLocation'))
    row(game,'清除所有尸体','RemoveAllCorpses',lambda:app.execute('RemoveAllCorpses'))
    row(game,'恢复自然天气','ClearWeather',lambda:app.execute('ClearWeather'))
    physics=section('物理','⚑')
    row(physics,'增加时间（秒）','AddTime',lambda:app.parameter('AddTime'),[],'3600')
    row(physics,'随机时间','RandomizeTime',lambda:app.execute('RandomizeTime'))
    for title in ('超级速度','低重力','超级跳跃','无限耐力'):
        row(physics,title,'toggle:'+title,lambda key=title:app.flip(key),toggle=True)
    tele=section('传送','◈')
    row(tele,'传送地点','TeleportTo',lambda:app.parameter('TeleportTo'),LOCATIONS)
    challenge=section('挑战模式','♨')
    row(challenge,'生成尸潮','SpawnHorde',lambda:app.parameter('SpawnHorde'),[],'5')
    # Same-page filters keep all controls on this page, and default to showing everything.
    filters=[None,{'常用置顶','玩家','属性与状态'}, {'物品与配方','载具'}, {'物理'}, {'游戏','传送'}, {'挑战模式'}]
    def select_filter(index):
        for title,card in sections:
            card.pack_forget()
        for title,card in sections:
            if filters[index] is None or title in filters[index]:card.pack(fill='x',pady=(0,14))
        canvas.yview_moveto(0)
    for index,button in enumerate([x for x in nav.winfo_children() if isinstance(x,Button)]):
        button.command=lambda i=index:select_filter(i)
