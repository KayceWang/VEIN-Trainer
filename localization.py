"""界面语言资源；不改变游戏本身的语言或内部编号。"""
import json
from pathlib import Path

LANGUAGES = {'zh':'中文', 'en':'English', 'es':'Español', 'fr':'Français', 'ru':'Русский'}
LANG = 'zh'
THEME = 'dark'
SETTINGS = Path(__file__).parent / '界面设置.json'
ROWS = r'''
正在执行：|Executing: |Ejecutando: |Exécution : |Выполнение: 
游戏已接受操作。请核对效果。|The game accepted the action. Check the result.|El juego aceptó la acción. Comprueba el resultado.|Le jeu a accepté l’action. Vérifiez le résultat.|Игра приняла действие. Проверьте результат.
不支持的直接操作。|Unsupported direct action.|Acción directa no compatible.|Action directe non prise en charge.|Неподдерживаемое прямое действие.
游戏线程不匹配，已停止直接操作。|Game thread mismatch; direct action stopped.|El hilo del juego no coincide; acción detenida.|Le thread du jeu ne correspond pas ; action arrêtée.|Поток игры не совпадает; действие остановлено.
另一个修改器窗口已连接，请先关闭旧窗口。|Another trainer is connected. Close it first.|Otro entrenador está conectado. Ciérralo primero.|Un autre entraîneur est connecté. Fermez-le d’abord.|Другой трейнер уже подключён. Сначала закройте его.
角色或世界已变化，请重新连接。|Player or world changed. Reconnect.|El personaje o mundo cambió. Vuelve a conectar.|Le personnage ou le monde a changé. Reconnectez-vous.|Персонаж или мир изменился. Подключитесь заново.
游戏未接受这项操作，请检查目标及当前世界。|The game rejected this action. Check the target and world.|El juego rechazó la acción. Comprueba el objetivo y el mundo.|Le jeu a refusé cette action. Vérifiez la cible et le monde.|Игра отклонила действие. Проверьте цель и мир.
准备就绪。快捷键在游戏或修改器位于前台时生效。持续功能开关有不同提示音。|Ready. Hotkeys work with the game or trainer focused. Toggles have distinct sounds.|Listo. Los atajos funcionan en el juego o entrenador. Los interruptores tienen sonidos distintos.|Prêt. Les raccourcis fonctionnent dans le jeu ou l’entraîneur. Les interrupteurs ont des sons distincts.|Готово. Клавиши работают в игре или трейнере. Переключатели имеют разные звуки.
请先进入游戏世界|Enter the game world first|Entra primero en el mundo del juego|Entrez d’abord dans le monde du jeu|Сначала войдите в игровой мир
语言：|Language:|Idioma:|Langue :|Язык:
无敌模式|God mode|Invencibilidad|Invincibilité|Неуязвимость
VEIN修改器|VEIN Trainer|VEIN Trainer|VEIN Trainer|VEIN Трейнер
自定义|Customize|Personalizar|Personnaliser|Настройка
全部|All|Todo|Tout|Все
辅助|Assist|Asistencia|Assistance|Помощь
便捷|Ease|Comodidad|Confort|Удобство
优化|Refine|Mejoras|Amélioration|Улучшения
沙盒|Sandbox|Sandbox|Bac à sable|Песочница
挑战|Challenge|Desafío|Défi|Испытание
刷取物品|Spawn items|Crear objetos|Créer des objets|Создать предметы
开始修改|Start|Iniciar|Démarrer|Запустить
正在运行|Playing|En ejecución|En cours|Работает
正在检查游戏…|Checking game…|Buscando el juego…|Recherche du jeu…|Проверка игры…
已找到 VEIN 游戏窗口|VEIN detected|VEIN detectado|VEIN détecté|VEIN найден
未找到唯一的 VEIN 窗口，请先启动游戏|Start one VEIN instance|Inicia una instancia de VEIN|Lancez une instance de VEIN|Запустите один экземпляр VEIN
常用置顶|Pinned|Fijados|Épinglés|Закреплённое
玩家|Player|Jugador|Joueur|Игрок
物品与配方|Inventory|Inventario|Inventaire|Инвентарь
属性与状态|Stats|Atributos|Statistiques|Характеристики
载具|Vehicles|Vehículos|Véhicules|Транспорт
游戏|Game|Juego|Jeu|Игра
物理|Physics|Física|Physique|Физика
传送|Teleport|Teletransporte|Téléportation|Телепортация
挑战模式|Challenge mods|Desafíos|Défis|Испытания
恢复手持物品耐久|Repair held item|Reparar objeto en mano|Réparer l’objet tenu|Починить предмет в руках
修复手持物品|Repair held item|Reparar objeto en mano|Réparer l’objet tenu|Починить предмет в руках
无限耐力|Infinite stamina|Resistencia infinita|Endurance infinie|Бесконечная выносливость
超级速度|Super speed|Supervelocidad|Super vitesse|Суперскорость
低重力|Low gravity|Gravedad baja|Gravité réduite|Низкая гравитация
超级跳跃|Super jump|Supersalto|Super saut|Суперпрыжок
已开启|ON|ACTIVO|ACTIF|ВКЛ
已关闭|OFF|INACTIVO|INACTIF|ВЫКЛ
开启|Enable|Activar|Activer|Вкл.
关闭|Disable|Desactivar|Désactiver|Выкл.
应用|Apply|Aplicar|Appliquer|Применить
设置快捷键|Set hotkey|Atajo|Raccourci|Клавиша
治疗角色|Heal player|Curar jugador|Soigner le joueur|Вылечить игрока
治疗所有玩家|Heal everyone|Curar a todos|Soigner tout le monde|Вылечить всех
给予每种物品|Give every item|Dar cada objeto|Donner tous les objets|Выдать все предметы
学习所有配方|Learn every recipe|Aprender recetas|Apprendre les recettes|Изучить все рецепты
学习所有建造|Learn every build object|Aprender construcciones|Apprendre les constructions|Изучить постройки
增加经验|Add XP|Añadir experiencia|Ajouter de l’XP|Добавить опыт
设置状态|Set condition|Establecer estado|Définir l’état|Задать состояние
给予车辆钥匙|Give vehicle key|Dar llave del vehículo|Donner la clé du véhicule|Выдать ключ от транспорта
给予目标钥匙|Give target key|Dar llave del objetivo|Donner la clé de la cible|Выдать ключ от цели
修复轮胎破损|Repair tires|Reparar neumáticos|Réparer les pneus|Починить шины
解锁目标|Unlock target|Desbloquear objetivo|Déverrouiller la cible|Отпереть цель
撬开目标|Lockpick target|Forzar cerradura|Crocheter la cible|Взломать замок
设置天气|Set weather|Cambiar clima|Changer la météo|Задать погоду
发现所有地点|Discover every location|Descubrir lugares|Découvrir tous les lieux|Открыть все места
清除所有尸体|Remove all corpses|Eliminar cadáveres|Retirer les cadavres|Убрать все трупы
恢复自然天气|Reset weather|Restaurar clima|Rétablir la météo|Сбросить погоду
增加时间（秒）|Add time (seconds)|Añadir tiempo (segundos)|Ajouter du temps (secondes)|Добавить время (секунды)
随机时间|Randomize time|Hora aleatoria|Heure aléatoire|Случайное время
传送地点|Teleport location|Destino|Destination|Место телепортации
生成尸潮|Spawn horde|Crear horda|Créer une horde|Создать орду
晴天|Clear|Despejado|Dégagé|Ясно
下雨|Rain|Lluvia|Pluie|Дождь
暴风雪|Blizzard|Ventisca|Blizzard|Метель
白天模式|Light mode|Modo claro|Mode clair|Светлая тема
夜间模式|Dark mode|Modo oscuro|Mode sombre|Тёмная тема
备份存档|Back up saves|Copiar partidas|Sauvegarder les parties|Резервная копия
使用说明|Help|Ayuda|Aide|Справка
保存|Save|Guardar|Enregistrer|Сохранить
清除绑定|Clear binding|Quitar atajo|Effacer le raccourci|Убрать клавишу
取消|Cancel|Cancelar|Annuler|Отмена
请按下要使用的快捷键|Press your shortcut|Pulsa el atajo deseado|Appuyez sur le raccourci|Нажмите сочетание клавиш
支持 F1–F12 或 Ctrl / Alt 加字母、数字。\n按键后点击保存；冲突时会提示，不覆盖其他功能。|F1–F12 or Ctrl / Alt + a letter or number.\nPress keys and click Save. Conflicts are rejected.|F1–F12 o Ctrl / Alt + letra o número.\nPulsa y guarda. Se rechazan conflictos.|F1–F12 ou Ctrl / Alt + lettre ou chiffre.\nAppuyez puis enregistrez. Les conflits sont refusés.|F1–F12 или Ctrl / Alt + буква или цифра.\nНажмите клавиши и сохраните. Конфликты отклоняются.
请先回到正常游戏画面，再点击顶部“开始修改”。|Return to gameplay, then click Start.|Vuelve al juego y pulsa Iniciar.|Revenez au jeu puis cliquez sur Démarrer.|Вернитесь в игру и нажмите «Запустить».
已开始：可点击功能，或切回游戏使用已设置的快捷键。|Ready. Use controls or return to the game to use hotkeys.|Listo. Usa los controles o los atajos dentro del juego.|Prêt. Utilisez les commandes ou les raccourcis dans le jeu.|Готово. Используйте кнопки или клавиши в игре.
已停止：快捷键不再执行，持续功能已关闭并恢复原值。|Stopped. Hotkeys paused and continuous options restored.|Detenido. Atajos pausados y valores restaurados.|Arrêté. Raccourcis suspendus et valeurs rétablies.|Остановлено. Клавиши отключены, исходные значения восстановлены.
准备就绪。快捷键仅在游戏位于前台时生效。持续功能开关有不同提示音。|Ready. Hotkeys work only while VEIN is focused. ON and OFF have different sounds.|Listo. Los atajos solo funcionan en VEIN. Activar y desactivar tienen sonidos distintos.|Prêt. Les raccourcis fonctionnent dans VEIN. Sons distincts pour activer et désactiver.|Готово. Клавиши работают только в VEIN. Для включения и выключения разные звуки.
中文物品库|Item catalog|Catálogo de objetos|Catalogue d’objets|Каталог предметов
中文物品库 · 选择物品后直接添加|Item catalog · select and add|Catálogo · selecciona y añade|Catalogue · sélectionner et ajouter|Каталог · выберите и добавьте
搜索物品|Search items|Buscar objetos|Chercher des objets|Поиск предметов
清空|Clear|Limpiar|Effacer|Очистить
物品名称|Item name|Nombre del objeto|Nom de l’objet|Название предмета
分类|Category|Categoría|Catégorie|Категория
数量|Quantity|Cantidad|Quantité|Количество
一键添加|Add item|Añadir objeto|Ajouter l’objet|Добавить предмет
请先选中一种物品|Select an item first|Selecciona un objeto|Sélectionnez un objet|Сначала выберите предмет
没有匹配结果，请更换关键词或分类。|No matches. Change the search or category.|Sin resultados. Cambia la búsqueda o categoría.|Aucun résultat. Modifiez la recherche ou catégorie.|Нет результатов. Измените поиск или категорию.
已选择：|Selected: |Seleccionado: |Sélectionné : |Выбрано: 
所选物品：|Selected item: |Objeto: |Objet : |Предмет: 
找到 {count} 种物品|{count} items found|{count} objetos encontrados|{count} objets trouvés|Найдено предметов: {count}
内置 {count} 种真实物品 · 选择分类或输入中文搜索|{count} game items · choose a category or search|{count} objetos · elige categoría o busca|{count} objets · choisissez une catégorie ou cherchez|{count} предметов · выберите категорию или выполните поиск
物品名称沿用游戏中文，支持中文和内部编号搜索。|Item names follow the Chinese game catalog. Search by Chinese name or internal ID.|Los nombres siguen el catálogo chino. Busca por nombre chino o ID.|Les noms suivent le catalogue chinois. Recherche par nom chinois ou ID.|Названия из китайского каталога игры. Поиск по китайскому имени или ID.
全部物品|All items|Todos los objetos|Tous les objets|Все предметы
交易|Trading|Comercio|Commerce|Торговля
体质|Vitality|Vitalidad|Vitalité|Живучесть
农耕|Farming|Agricultura|Agriculture|Фермерство
制作|Crafting|Fabricación|Fabrication|Изготовление
力量|Strength|Fuerza|Force|Сила
医疗|Medical|Medicina|Médecine|Медицина
建造|Construction|Construcción|Construction|Строительство
开锁|Lockpicking|Ganzúas|Crochetage|Взлом замков
投掷|Throwing|Lanzamiento|Lancer|Метание
拆解|Dismantling|Desmontaje|Démontage|Разборка
搜刮|Scavenging|Recolección|Récupération|Поиск припасов
敏捷|Agility|Agilidad|Agilité|Ловкость
机械|Mechanical|Mecánica|Mécanique|Механика
武器操控|Weapon handling|Manejo de armas|Maniement des armes|Владение оружием
潜行|Sneaking|Sigilo|Discrétion|Скрытность
烹饪|Cooking|Cocina|Cuisine|Кулинария
电工|Electrical|Electricidad|Électricité|Электрика
社交|Sociability|Sociabilidad|Sociabilité|Общение
维修|Repair|Reparación|Réparation|Ремонт
驾驶|Driving|Conducción|Conduite|Вождение
已发送：|Sent: |Enviado: |Envoyé : |Отправлено: 
已开启。| enabled.| activado.| activé.| включено.
已关闭。| disabled.| desactivado.| désactivé.| выключено.
操作中止：|Operation stopped: |Operación detenida: |Opération arrêtée : |Операция остановлена: 
无法开始：|Cannot start: |No se puede iniciar: |Démarrage impossible : |Не удалось запустить: 
游戏版本变化，已停止数据修改。请重新适配。|Game version changed. Data editing is disabled until updated.|Versión del juego cambiada. Edición desactivada hasta actualizar.|Version du jeu modifiée. Modification désactivée en attendant une mise à jour.|Версия игры изменилась. Изменения отключены до обновления.
数据修改仅支持本机单机世界，请退出联机。|Data editing supports local single player only.|Solo se admite una partida local individual.|Seul le mode solo local est pris en charge.|Поддерживается только локальная одиночная игра.
请先把需要修复的武器或工具拿在手里，再关闭背包。|Hold the weapon or tool you want to repair, then close the inventory.|Sostén el arma o herramienta y cierra el inventario.|Tenez l’arme ou l’outil puis fermez l’inventaire.|Возьмите оружие или инструмент в руки и закройте инвентарь.
未找到唯一的游戏窗口。|One game window is required.|Se requiere una ventana del juego.|Une seule fenêtre de jeu est requise.|Требуется одно окно игры.
该快捷键已被系统或其他程序占用，请换一个。|Shortcut already in use. Choose another.|Atajo ocupado. Elige otro.|Raccourci déjà utilisé. Choisissez-en un autre.|Сочетание занято. Выберите другое.
该快捷键已分配给另一项功能。|Shortcut assigned to another option.|Atajo asignado a otra función.|Raccourci affecté à une autre fonction.|Сочетание назначено другой функции.
请用 F1–F12，或 Ctrl / Alt / Shift 加字母、数字。|Use F1–F12 or modifiers with a letter or number.|Usa F1–F12 o modificadores con letra o número.|Utilisez F1–F12 ou modificateurs avec lettre ou chiffre.|Используйте F1–F12 или модификаторы с буквой или цифрой.
普通字母请搭配 Ctrl 或 Alt，避免打字时误触。|Use Ctrl or Alt with letters to avoid accidental activation.|Usa Ctrl o Alt con letras para evitar activación accidental.|Utilisez Ctrl ou Alt avec les lettres pour éviter les activations accidentelles.|Используйте Ctrl или Alt с буквами во избежание случайных срабатываний.
：快捷键已清除。|: shortcut cleared.|: atajo eliminado.| : raccourci effacé.|: сочетание удалено.
：快捷键已保存。|: shortcut saved.|: atajo guardado.| : raccourci enregistré.|: сочетание сохранено.
参数需要调整|Check parameters|Revisar parámetros|Vérifier les paramètres|Проверьте параметры
数量需要调整|Check quantity|Revisar cantidad|Vérifier la quantité|Проверьте количество
等待游戏回执。|Waiting for game response.|Esperando respuesta del juego.|En attente de réponse du jeu.|Ожидание ответа игры.
游戏日志已记录指令；请在游戏中核对效果。|The game logged the command. Check the effect in game.|El juego registró el comando. Comprueba el efecto.|Le jeu a enregistré la commande. Vérifiez son effet.|Игра записала команду. Проверьте результат в игре.
未获得明确日志回执，请查看游戏控制台；不要直接重复切换类功能。|No explicit log response. Check the game console before repeating.|Sin respuesta explícita. Revisa la consola antes de repetir.|Pas de réponse explicite. Vérifiez la console avant de répéter.|Нет явного ответа. Проверьте консоль перед повтором.
游戏返回拒绝或未知指令，请检查权限及参数。|Command rejected or unknown. Check permissions and parameters.|Comando rechazado o desconocido. Revisa permisos y parámetros.|Commande refusée ou inconnue. Vérifiez les droits et paramètres.|Команда отклонена или неизвестна. Проверьте права и параметры.
尚未发送：|Not sent: |No enviado: |Non envoyé : |Не отправлено: 
发送中止：|Sending stopped: |Envío detenido: |Envoi arrêté : |Отправка остановлена: 
请等待上一条操作完成后再点击。|Wait for the previous operation.|Espera a que termine la operación.|Attendez la fin de l’opération.|Дождитесь завершения предыдущей операции.
修复尚未生效，当前耐久 |Repair not confirmed. Durability: |Reparación no confirmada. Durabilidad: |Réparation non confirmée. Durabilité : |Ремонт не подтверждён. Прочность: 
耐久已核验：|Durability verified: |Durabilidad verificada: |Durabilité vérifiée : |Прочность проверена: 
无限耐力已停止：|Infinite stamina stopped: |Resistencia infinita detenida: |Endurance infinie arrêtée : |Бесконечная выносливость отключена: 
角色没有该状态，无需清除。|Condition not present; nothing to clear.|Estado ausente; nada que borrar.|État absent ; rien à effacer.|Состояние отсутствует, удаление не требуется.
请先确认游戏处于正常游玩画面。|Return to normal gameplay first.|Vuelve primero a la partida.|Revenez d’abord au jeu.|Сначала вернитесь в игру.
'''
ROWS += r'''
制作图纸与食谱|Schematics and recipes|Planos y recetas|Plans et recettes|Чертежи и рецепты
医疗用品|Medical supplies|Material médico|Matériel médical|Медицинские припасы
工具与设备|Tools and equipment|Herramientas y equipos|Outils et équipement|Инструменты и оборудование
开发测试物品|Developer test items|Objetos de prueba|Objets de test|Тестовые предметы
弹药与配件|Ammo and attachments|Munición y accesorios|Munitions et accessoires|Боеприпасы и обвесы
影音物品|Media|Multimedia|Multimédia|Медиа
技能书与杂志|Skill books and magazines|Libros y revistas|Livres et magazines|Книги навыков и журналы
服装与护具|Clothing and armor|Ropa y protección|Vêtements et protections|Одежда и броня
材料与制作零件|Crafting materials|Materiales de fabricación|Matériaux de fabrication|Материалы для изготовления
武器|Weapons|Armas|Armes|Оружие
清洁与个人护理|Cleaning and care|Limpieza y cuidado|Nettoyage et soins|Уборка и уход
烟花|Fireworks|Fuegos artificiales|Feux d’artifice|Фейерверки
生活杂物与摆件|Household items|Objetos domésticos|Objets domestiques|Бытовые предметы
种子与农业|Seeds and farming|Semillas y agricultura|Graines et agriculture|Семена и земледелие
药物与烟酒|Drugs and tobacco|Drogas y tabaco|Drogues et tabac|Препараты и табак
货币|Currency|Moneda|Monnaie|Валюта
车辆配件|Vehicle parts|Piezas de vehículos|Pièces de véhicules|Запчасти транспорта
钥匙|Keys|Llaves|Clés|Ключи
食物与食材|Food and ingredients|Comida e ingredientes|Nourriture et ingrédients|Еда и ингредиенты
饮料与液体|Drinks and liquids|Bebidas y líquidos|Boissons et liquides|Напитки и жидкости
鱼类与水产|Fish and seafood|Pescado y marisco|Poissons et fruits de mer|Рыба и морепродукты
备份校验完成：|Backup verified: |Copia verificada: |Sauvegarde vérifiée : |Копия проверена: 
备份未完成：|Backup incomplete: |Copia incompleta: |Sauvegarde incomplète : |Копирование не завершено: 
开始备份，请保持游戏位于主菜单，避免自动保存。|Backing up. Keep the game at the main menu to avoid autosaving.|Copiando. Mantén el menú principal para evitar autoguardado.|Sauvegarde. Restez au menu principal pour éviter l’enregistrement automatique.|Копирование. Оставайтесь в главном меню во избежание автосохранения.
手持物品发生变化，无法核对，请重新修复。|Held item changed. Repair again to verify.|Cambió el objeto en mano. Repite la reparación.|L’objet tenu a changé. Réparez-le à nouveau.|Предмет в руках изменился. Повторите ремонт.
无法核验耐久：|Cannot verify durability: |No se pudo verificar durabilidad: |Impossible de vérifier la durabilité : |Не удалось проверить прочность: 
未找到唯一的本地玩家。|One local player is required.|Se requiere un jugador local.|Un seul joueur local est requis.|Требуется один локальный игрок.
角色尚未进入可操作世界。|The character is not in a playable world.|El personaje no está en una partida activa.|Le personnage n’est pas dans un monde jouable.|Персонаж ещё не в игровом мире.
游戏数据已变化，请重新连接。|Game data changed. Reconnect.|Datos del juego cambiados. Vuelve a conectar.|Données du jeu modifiées. Reconnectez-vous.|Данные игры изменились. Подключитесь заново.
请先选中一种物品|Select an item first|Selecciona un objeto|Sélectionnez un objet|Сначала выберите предмет
请使用普通非负数字，最多六位小数。|Use a nonnegative number, up to six decimals.|Usa un número no negativo con hasta seis decimales.|Utilisez un nombre positif ou nul, six décimales maximum.|Введите неотрицательное число, не более шести знаков после запятой.
物品数量必须是整数。|Quantity must be a whole number.|La cantidad debe ser entera.|La quantité doit être entière.|Количество должно быть целым числом.
请选择状态并输入普通数字。|Select a condition and enter a number.|Elige un estado e introduce un número.|Choisissez un état et saisissez un nombre.|Выберите состояние и введите число.
该状态允许范围：|Allowed range: |Rango permitido: |Plage autorisée : |Допустимый диапазон: 
数值超出范围：|Value out of range: |Valor fuera de rango: |Valeur hors plage : |Значение вне диапазона: 
已设置|Set: |Establecido: |Défini : |Установлено: 
，数据回读已核验。|. Readback verified.|. Lectura verificada.|. Relecture vérifiée.|. Проверено чтением.
请检查游戏|Check the game|Revisa el juego|Vérifiez le jeu|Проверьте игру
'''
ROWS += r'''
LSD致幻|LSD effects|Efectos de LSD|Effets du LSD|Эффект ЛСД
中毒|Poisoned|Envenenado|Empoisonné|Отравление
亢奋|Stimulated|Estimulado|Stimulé|Стимуляция
享用了美食|Well fed|Bien alimentado|Bien nourri|Сытость
做了噩梦|Nightmare|Pesadilla|Cauchemar|Кошмар
冰毒|Meth effects|Efectos de metanfetamina|Effets de méthamphétamine|Эффект метамфетамина
冻伤|Frostbite|Congelación|Gelures|Обморожение
割伤|Cut wound|Corte|Coupure|Резаная рана
力竭|Exertion|Agotamiento|Épuisement|Истощение
压力|Stress|Estrés|Stress|Стресс
口渴|Thirst|Sed|Soif|Жажда
可卡因|Cocaine|Cocaína|Cocaïne|Кокаин
咬伤|Bite wound|Mordedura|Morsure|Укус
困乏|Lethargy|Letargo|Léthargie|Вялость
失温|Hypothermia|Hipotermia|Hypothermie|Переохлаждение
嵌入的子弹|Lodged bullet|Bala incrustada|Balle logée|Застрявшая пуля
嵌入的弹片|Lodged shrapnel|Metralla incrustada|Éclat logé|Застрявший осколок
巨型猪草|Giant hogweed|Perejil gigante|Berce du Caucase|Борщевик
异物移除后的伤口|Dislodged wound|Herida tras extracción|Plaie après extraction|Рана после извлечения
恐慌|Panic|Pánico|Panique|Паника
戒断反应|Withdrawal|Abstinencia|Sevrage|Абстиненция
手臂骨折|Broken arm|Brazo roto|Bras cassé|Перелом руки
手部烧伤|Burnt hand|Mano quemada|Main brûlée|Ожог руки
抗抑郁|Antidepressant effect|Efecto antidepresivo|Effet antidépresseur|Эффект антидепрессанта
抗生素|Antibiotic|Antibiótico|Antibiotique|Антибиотик
挫伤|Blunt wound|Contusión|Contusion|Ушиб
晒伤|Sunburn|Quemadura solar|Coup de soleil|Солнечный ожог
服用了止痛药|Painkiller effect|Efecto analgésico|Effet antalgique|Обезболивание
松果菊|Coneflower|Equinácea|Échinacée|Эхинацея
毛蕊花|Common mullein|Gordolobo|Molène|Коровяк
气味|Scent|Olor|Odeur|Запах
涂了油的双手|Oily hands|Manos aceitosas|Mains huileuses|Масло на руках
潮湿|Wetness|Humedad|Humidité|Влажность
烧伤|Burned|Quemadura|Brûlure|Ожог
生病|Sick|Enfermo|Malade|Болезнь
疲劳|Tiredness|Cansancio|Fatigue|Усталость
疼痛|Pain|Dolor|Douleur|Боль
神智恍惚|Stoned|Aturdido|État second|Одурманивание
窒息|Asphyxiating|Asfixia|Asphyxie|Удушье
精力透支|Energy crash|Bajón de energía|Chute d’énergie|Упадок сил
紫草|Comfrey|Consuelda|Consoude|Окопник
美味牛肝菌|King bolete|Boleto comestible|Cèpe de Bordeaux|Белый гриб
肮脏|Dirtiness|Suciedad|Saleté|Грязь
脑震荡|Concussion|Conmoción cerebral|Commotion cérébrale|Сотрясение
脚踝扭伤|Sprained ankle|Esguince de tobillo|Entorse de la cheville|Растяжение лодыжки
脚部感染|Foot infection|Infección del pie|Infection du pied|Инфекция стопы
腿部骨折|Broken leg|Pierna rota|Jambe cassée|Перелом ноги
艾草|Mugwort|Artemisa|Armoise|Полынь
蓍草|Yarrow|Milenrama|Achillée|Тысячелистник
血液中毒|Blood poisoning|Intoxicación sanguínea|Empoisonnement du sang|Заражение крови
负重|Encumbrance|Carga|Encombrement|Перегрузка
过度饱腹|Overfed|Sobrealimentado|Trop nourri|Переедание
过敏性休克|Anaphylactic shock|Choque anafiláctico|Choc anaphylactique|Анафилактический шок
过热|Overheating|Sobrecalentamiento|Surchauffe|Перегрев
醉酒|Drunk|Ebrio|Ivresse|Опьянение
野蒜|Wild garlic|Ajo silvestre|Ail sauvage|Черемша
防晒霜|Sunscreen|Protector solar|Crème solaire|Солнцезащитный крем
食物中毒|Food poisoning|Intoxicación alimentaria|Intoxication alimentaire|Пищевое отравление
饥饿|Hunger|Hambre|Faim|Голод
饮水过量|Overhydrated|Sobrehidratado|Surhydratation|Избыток воды
高血糖|High blood sugar|Hiperglucemia|Hyperglycémie|Высокий сахар
鼠尾草|Sage|Salvia|Sauge|Шалфей
'''
TABLE = {}
for line in ROWS.strip().splitlines():
    if not line.strip():continue
    parts = [part.replace('\\n','\n') for part in line.split('|')]
    assert len(parts) == 5, line
    TABLE[parts[0]] = dict(zip(LANGUAGES, parts))
REVERSE = {value:key for key,row in TABLE.items() for value in row.values()}


def tr(text, **values):
    source = REVERSE.get(text, text)
    if source in TABLE:
        result = TABLE[source][LANG]
    else:
        result = source
        for key in sorted(TABLE, key=len, reverse=True):
            if key in result:
                result = result.replace(key, TABLE[key][LANG])
    return result.format(**values) if values else result


def load():
    global LANG, THEME
    try:
        saved = json.loads(SETTINGS.read_text(encoding='utf-8'))
        LANG = saved.get('language', 'zh') if saved.get('language') in LANGUAGES else 'zh'
        THEME = saved.get('theme', 'dark') if saved.get('theme') in ('dark','light') else 'dark'
    except (OSError,ValueError,AttributeError):
        LANG, THEME = 'zh', 'dark'


def save():
    temp = SETTINGS.with_suffix('.tmp')
    temp.write_text(json.dumps({'language':LANG,'theme':THEME},ensure_ascii=False),encoding='utf-8')
    temp.replace(SETTINGS)


def translate_tree(widget):
    import tkinter as tk
    from tkinter import ttk
    if isinstance(widget, tk.Toplevel):
        widget.title(tr(widget.title()))
    if 'text' in widget.keys() and not str(widget.cget('textvariable') if 'textvariable' in widget.keys() else ''):
        text = widget.cget('text')
        if text:
            if not hasattr(widget,'_source_text'):
                widget._source_text=REVERSE.get(str(text),str(text))
            widget.configure(text=tr(widget._source_text))
    if isinstance(widget, tk.Canvas):
        if not hasattr(widget,'_text_sources'):widget._text_sources={}
        for item in widget.find_all():
            if widget.type(item)=='text':
                current=widget.itemcget(item,'text')
                source=widget._text_sources.setdefault(item,REVERSE.get(current,current))
                widget.itemconfigure(item,text=tr(source))
        if hasattr(widget, 'fit_text'):
            widget.fit_text()
    if isinstance(widget, ttk.Treeview):
        for column in widget['columns']:
            widget.heading(column,text=tr(widget.heading(column,'text')))
    for child in widget.winfo_children():
        translate_tree(child)
