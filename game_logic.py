import os

# Конфигурация уровней (для карты уровней)
LEVELS_STRUCTURE = {
    "Easy": {
        "tasks_count": 7, 
        "title": "ЛЁГКИЙ УРОВЕНЬ",
        "bg_color": [0.1, 0.2, 0.4, 1]
    },
    "Medium": {
        "tasks_count": 8,
        "title": "СРЕДНИЙ УРОВЕНЬ",
        "bg_color": [0.2, 0.1, 0.3, 1]
    },
    "Hard": {
        "tasks_count": 8,
        "title": "СЛОЖНЫЙ УРОВЕНЬ",
        "bg_color": [0.1, 0.1, 0.2, 1]
    }
}

# --- БАЗА ДАННЫХ УПРАЖНЕНИЙ ---
# Здесь мы храним всё: Инструкции, Ребусы, Тесты и Диктанты
REBUS_DATA = {
    "Easy": {
        # 1. ТЕОРИЯ (Урок)
        "1": {
            "type": "lesson",
            "steps": {
                "1": {"img": "easy_1_1.jpg", "hint": "КАК РАЗГАДЫВАТЬ РЕБУСЫ?"},
                "2": {"img": "easy_1_2.jpg", "hint": "КАК РАЗГАДЫВАТЬ РЕБУСЫ?"},
                "3": {"img": "easy_1_3.jpg", "hint": "КАК РАЗГАДЫВАТЬ РЕБУСЫ?"},
                "4": {"img": "easy_1_4.jpg", "hint": "КАК РАЗГАДЫВАТЬ РЕБУСЫ?"},
                "5": {"img": "easy_1_5.jpg", "hint": "КАК РАЗГАДЫВАТЬ РЕБУСЫ?"}
            }
        },
        
        # 2. РЕБУС (Первый блок)
        "2": {
            "type": "rebus",
            "steps": {
                "1": {"img": "easy_2_1.jpg", "ans": "мороз", "hint": "Готов к первой маленькой победе?"},
                "2": {"img": "easy_2_2.jpg", "ans": "лужа", "hint": "Сможешь разгадать это с первого взгляда?"},
                "3": {"img": "easy_2_3.jpg", "ans": "скрипка", "hint": "Что за слово спряталось за этими картинками?"},
                "4": {"img": "easy_2_4.jpg", "ans": "роша", "hint": "Видишь ли ты решение, скрытое на поверхности?"},
                "5": {"img": "easy_2_5.jpg", "ans": "снежки", "hint": "Хватит ли тебе пары секунд для ответа?"}
            }
        },

        # 3. РЕБУС (Второй блок)
        "3": {
            "type": "rebus",
            "steps": {
                "1": {"img": "easy_3_1.jpg", "ans": "роса", "hint": "Чувствуешь, как просыпается твоя логика?"},
                "2": {"img": "easy_3_2.jpg", "ans": "гриб", "hint": "Готов ли ты сделать шаг в мир загадок?"},
                "3": {"img": "easy_3_3.jpg", "ans": "пальто", "hint": "Сможешь ли ты найти связь там, где другие её не видят?"},
                "4": {"img": "easy_3_4.jpg", "ans": "след", "hint": "Веришь в свою интуицию сегодня?"},
                "5": {"img": "easy_3_5.jpg", "ans": "касса", "hint": "Что, если ответ проще, чем тебе кажется?"}
            }
        },

        # 4. РЕБУС (Третий блок)
        "4": {
            "type": "rebus",
            "steps": {
                "1": {"img": "easy_4_1.jpg", "ans": "объявление", "hint": "Куда заведет тебя твоя фантазия на этот раз?"},
                "2": {"img": "easy_4_2.jpg", "ans": "звездный", "hint": "Разве этот ребус сможет тебя остановить?"},
                "3": {"img": "easy_4_3.jpg", "ans": "устный", "hint": "Удастся ли тебе распутать этот узелок из букв?"},
                "4": {"img": "easy_4_4.jpg", "ans": "солнце", "hint": "Поймешь ли ты намек, скрытый в деталях?"},
                "5": {"img": "easy_4_5.jpg", "ans": "честный", "hint": "Сколько времени тебе нужно на этот вызов?"}
            }
        },

        # 5. РЕБУС (Четвертый блок)
        "5": {
            "type": "rebus",
            "steps": {
                "1": {"img": "easy_5_1.jpg", "ans": "льет", "hint": "Сможешь ли ты сохранить концентрацию?"},
                "2": {"img": "easy_5_2.jpg", "ans": "съезд", "hint": "Видишь ли ты логику в этом хаосе образов?"},
                "3": {"img": "easy_5_3.jpg", "ans": "день", "hint": "Что за тайна зашифрована в этом знаке?"},
                "4": {"img": "easy_5_4.jpg", "ans": "подъезд", "hint": "Готов ли твой мозг к серьезной нагрузке?"},
                "5": {"img": "easy_5_5.jpg", "ans": "вьюга", "hint": "Станешь ли ты мастером дешифровки сегодня?"}
            }
        },

        # 6. РЕБУС (Пятый блок)
        "6": {
            "type": "rebus",
            "steps": {
                "1": {"img": "easy_6_1.jpg", "ans": "майка", "hint": "Найдешь ли ты выход из этого лабиринта мыслей?"},
                "2": {"img": "easy_6_2.jpg", "ans": "пальто", "hint": "Способен ли ты заглянуть за рамки привычного?"},
                "3": {"img": "easy_6_3.jpg", "ans": "ягода", "hint": "Хватит ли у тебя терпения докопаться до истины?"},
                "4": {"img": "easy_6_4.jpg", "ans": "объезд", "hint": "Узнаешь ли ты слово, изменившее свой облик?"},
                "5": {"img": "easy_6_5.jpg", "ans": "подъем", "hint": "Сможешь ли ты обойти все ловушки этого уровня?"}
            }
        },

        "7": {  # Поставь нужный номер упражнения
            "type": "dictation",
            "full_text": "Летнее [ref=1][color=#ffcc00]со…нце[/color][/ref] ярко [ref=2][color=#ffcc00]осв…щает[/color][/ref] окрестности. В чаще леса поют птицы. Под [ref=3][color=#ffcc00]б…рёзами[/color][/ref] спрятались душистые ландыши. Маленький зверёк прыгнул с ветки на ветку. В воздухе [ref=4][color=#ffcc00]разл…вается[/color][/ref] запах травы. На листьях блестит роса. [ref=5][color=#ffcc00]Сер…це[/color][/ref] радуется такой красоте. Нужно беречь нашу природу.",
            "steps": {
                "1": {"ans": "л", "hint": "1"},
                "2": {"ans": "е", "hint": "2"},
                "3": {"ans": "е", "hint": "3"},
                "4": {"ans": "и", "hint": "4"},
                "5": {"ans": "д", "hint": "5"}
                }
            }
        }
    }
    

# --- ФУНКЦИИ ЛОГИКИ ---

def get_exercise_data(level, ex_id, step):
    """
    Загружает данные конкретного шага упражнения.
    Исправлено: теперь автоматически подтягивает 'full_text' для диктантов.
    """
    try:
        # Приводим уровень к формату "Easy", "Medium", "Hard"
        level_fixed = str(level).capitalize()
        
        # Подключаем REBUS_DATA (убедись, что этот словарь импортирован или находится в этом файле)
        lvl_dict = REBUS_DATA.get(level_fixed)
        if not lvl_dict:
            print(f"DEBUG: Уровень '{level_fixed}' не найден")
            return None
            
        ex_dict = lvl_dict.get(str(ex_id))
        if not ex_dict:
            print(f"DEBUG: Урок '{ex_id}' не найден")
            return None
            
        # Получаем данные конкретного шага из блока steps
        steps_dict = ex_dict.get("steps", {})
        step_data = steps_dict.get(str(step))
        
        if step_data:
            # Создаем копию данных шага, чтобы не испортить оригинал в словаре
            result = step_data.copy()
            
            # Добавляем тип упражнения из родительского блока
            result["type"] = ex_dict.get("type", "rebus")
            
            # ВАЖНО: Если это диктант, пробрасываем основной текст (full_text) в каждый шаг
            if result["type"] == "dictation":
                result["full_text"] = ex_dict.get("full_text") or ex_dict.get("text")
            
            return result
            
        return None
    except Exception as e:
        print(f"Ошибка в get_exercise_data: {e}")
        return None

def get_menu_data(level_name):
    lvl = str(level_name).strip()
    return LEVELS_STRUCTURE.get(lvl, LEVELS_STRUCTURE.get("Easy"))

def get_step_side(task_index):
    return "left" if int(task_index) % 2 != 0 else "right"

def get_exercise_type(level, ex_id):
    """Определяет текст для заголовка на карте уровней"""
    try:
        t = REBUS_DATA[level][str(ex_id)]["type"]
        types = {"lesson": "УРОК", "rebus": "РЕБУС", "test": "ТЕСТ", "dictation": "ДИКТАНТ"}
        return types.get(t, "ЗАДАНИЕ")
    except:
        return "УРОК"

def get_help_image_path(level, ex_id, step):
    """Ищет фото подсказки для конкретного шага или всего урока"""
    lvl = level.lower()
    
    # 1. Путь для конкретного шага
    specific_path = f"assets/levels/{lvl}/{ex_id}_step_{step}.jpg"
    if os.path.exists(specific_path):
        return specific_path
        
    # 2. Общее фото урока
    general_path = f"assets/levels/{lvl}/{ex_id}_help.jpg"
    if os.path.exists(general_path):
        return general_path
    
    # 3. Стандартная заглушка
    return "assets/images/default_help.jpg"


# --- РАБОТА С ФАЙЛОМ (7 ПАРАМЕТРОВ) ---
def save_all_data(name, level, dark_mode, day, month, year, progress):
    """
    Универсальное сохранение данных (7 параметров).
    Принудительно приводит типы к строкам для корректной записи.
    """
    try:
        # Приводим тему к формату "1" или "0" для стабильного чтения
        dm_str = "1" if str(dark_mode) in ["True", "1"] else "0"
        
        data_list = [
            str(name).strip(),
            str(level).strip(),
            dm_str,
            str(day).strip(),
            str(month).strip(),
            str(year).strip(),
            str(progress).strip()
        ]
        
        with open("user_data.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(data_list))
            
        print("DEBUG: Данные успешно сохранены в user_data.txt")
    except Exception as e:
        print(f"ОШИБКА СОХРАНЕНИЯ: {e}")

def load_all_data():
    """
    Надежное чтение данных. 
    Возвращает список из 7 элементов, конвертирует типы на лету.
    """
    path = "user_data.txt"
    # Стандартный прогресс в новом формате: 1-0|1-0|1-0
    default = ["Ученик", "Easy", False, "1", "Янв", "2026", "1-0|1-0|1-0"]
    
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            # Читаем все непустые строки
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        if len(lines) >= 7:
            # Превращаем "1"/"0" обратно в True/False для Kivy
            is_dark = lines[2] == "1"
            
            # На всякий случай исправляем старый формат прогресса ":" на "-"
            prog = lines[6].replace(":", "-")
            
            return [lines[0], lines[1], is_dark, lines[3], lines[4], lines[5], prog]
        else:
            print("DEBUG: Файл поврежден или содержит старые данные. Сброс.")
            return default
            
    except Exception as e:
        print(f"ОШИБКА ЧТЕНИЯ: {e}")
        return default

def get_stars_for_task(progress_str, task_id):
    """
    Извлекает звезды. 
    Исправлено: добавлена защита от некорректного формата строки прогресса.
    """
    try:
        if not progress_str or ":" not in progress_str:
            return 0
            
        parts = progress_str.split('|')
        for part in parts:
            if ":" in part:
                t_id, stars = part.split(':')
                if str(t_id) == str(task_id):
                    return int(stars)
    except:
        pass
    return 0