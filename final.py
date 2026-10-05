import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
import json
from kivy.app import App
from kivy.config import ConfigParser
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Line
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


from kivy.properties import ListProperty, DictProperty
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
try:
    from game_logic import load_all_data, save_all_data, get_rebus_step_data, get_exercise_type
except ImportError:
    print("Ошибка: Файл game_logic.py не найден или содержит ошибки!")
Window.size = (360, 640)

# Остальной код оставляем без изменений, он написан верно
def get_triple_gradient():
    texture = Texture.create(size=(1, 3), colorfmt='rgb')
    # Синий -> Голубой -> Белый
    buf = bytearray([20, 60, 140, 140, 200, 230, 255, 255, 255])
    texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
    return texture

class FixedWheel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effect_cls = 'DampedScrollEffect'
        self.scroll_type = ['content']
        self.bind(on_scroll_stop=self.snap_to_item)

    def snap_to_item(self, *args):
        if not self.children: return
        content = self.children[0]
        item_height = 40 
        max_scroll = content.height - self.height
        if max_scroll <= 0: return
        current_y_pixel = self.scroll_y * max_scroll
        target_idx = round(current_y_pixel / item_height)
        new_scroll_y = max(0, min(1, (target_idx * item_height) / max_scroll))
        Animation(scroll_y=new_scroll_y, d=0.2, t='out_quad').start(self)

def save_all_data(name, level, night, d, m, y, progress):
    """
    Сохраняет 7 параметров пользователя.
    night: передается как True/False (bool)
    progress: строка вида "1-3,2-0|1-0|1-0"
    """
    try:
        # night преобразуем в строку 'True' или 'False' для сохранения
        with open("user_data.txt", "w", encoding='utf-8') as f:
            f.write(f"{name}\n{level}\n{str(night)}\n{d}\n{m}\n{y}\n{str(progress)}")
        print("Данные успешно сохранены")
    except Exception as e:
        print(f"Критическая ошибка сохранения: {e}")

def load_all_data():
    """
    Загружает данные. Всегда возвращает 7 элементов нужных типов.
    """
    # ВАЖНО: стандартный прогресс теперь "1-0|1-0|1-0"
    default_values = ["Ученик", "Easy", False, "1", "Янв", "2026", "1-0|1-0|1-0"]
    
    if not os.path.exists("user_data.txt"):
        return default_values
    
    try:
        with open("user_data.txt", "r", encoding='utf-8') as f:
            # Читаем все строки и убираем пустые
            lines = [l.strip() for l in f.readlines() if l.strip()]
            
        if len(lines) >= 7:
            # Превращаем строку 'true'/'1' в настоящий bool (True/False)
            # Это критично для app.dark_mode в Kivy
            is_night = lines[2].lower() in ['true', '1', 't']
            
            prog = lines[6]
            # Авто-исправление старого формата, если он остался в файле
            if ":" in prog:
                prog = prog.replace(":", "-")
                
            return [lines[0], lines[1], is_night, lines[3], lines[4], lines[5], prog]
        
        elif len(lines) >= 6:
            # Если прогресса нет (старый файл), добавляем пустой прогресс
            is_night = lines[2].lower() in ['true', '1', 't']
            return [lines[0], lines[1], is_night, lines[3], lines[4], lines[5], "1-0|1-0|1-0"]
            
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
    
    return default_values


# Загружаем основной дизайн
# Загружаем основной дизайн
Builder.load_file('style.kv')
# Загружаем дизайн экрана упражнений отдельно
Builder.load_file('exercise.kv')

class SplashScreen(Screen):
    bg_texture = get_triple_gradient()
    loading_text = StringProperty("ЗАГРУЗКА")

    def on_enter(self, *args):
        logo = self.ids.logo_img
        # Анимация появления логотипа
        anim = Animation(opacity=1, duration=1)
        # Анимация "дыхания" (плавное изменение размера)
        breath = Animation(size_hint=(0.55, 0.55), d=1.5, t='in_out_quad') + \
                 Animation(size_hint=(0.5, 0.5), d=1.5, t='in_out_quad')
        breath.repeat = True
        
        anim.bind(on_complete=lambda *args: breath.start(logo))
        anim.start(logo)

        self.dot_count = 0
        self.ev = Clock.schedule_interval(self.update_dots, 0.5)
        # Ждем 3 секунды и проверяем данные
        Clock.schedule_once(self.finish_loading, 3)

    def update_dots(self, dt):
        self.dot_count = (self.dot_count + 1) % 4
        self.loading_text = "ЗАГРУЗКА" + "." * self.dot_count

    def finish_loading(self, dt):
        # Останавливаем точки
        if hasattr(self, 'ev'):
            Clock.unschedule(self.ev)
        
        # 1. Проверяем наличие файла
        if not os.path.exists("user_data.txt"):
            self.manager.current = 'register'
            return

        try:
            # 2. Пытаемся считать 7 параметров
            res = load_all_data()
            
            # Если данных меньше 7 (старый файл), отправляем на регистрацию для чистоты
            if len(res) < 7:
                self.manager.current = 'register'
                return

            name, level, night, d, m, y, progress = res
            
            # 3. Логика перехода
            if level == "None" or level == "":
                # Если зарегистрирован, но сложность не выбрана
                self.manager.current = 'menu'
            else:
                # Если всё готово — в дашборд
                self.manager.current = 'main_dashboard'
                
        except Exception as e:
            print(f"Ошибка загрузки в Splash: {e}")
            self.manager.current = 'register'
class RegisterScreen(Screen):
    bg_texture = ObjectProperty(None)
    selected_year = StringProperty("2026")

    def on_pre_enter(self, *args):
        self.bg_texture = get_triple_gradient()
        # Заполняем барабан годами, если он пуст
        if not self.ids.y_cont.children:
            for x in range(2026, 1949, -1):
                self.ids.y_cont.add_widget(Label(text=str(x), size_hint_y=None, height=40, color=(0,0,0,1)))
            for x in range(1, 32):
                self.ids.d_cont.add_widget(Label(text=str(x), size_hint_y=None, height=40, color=(0,0,0,1)))
            for x in ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]:
                self.ids.m_cont.add_widget(Label(text=x, size_hint_y=None, height=40, color=(0,0,0,1)))

    def get_center_value(self, container):
        """Вычисляет, какая надпись сейчас в центре барабана"""
        if not container.children: return "2026"
        sv = container.parent 
        kids = container.children[::-1] 
        idx = int((1 - max(0, min(1, sv.scroll_y))) * (len(kids) - 1))
        return kids[idx].text

    def save_user(self):
        name = self.ids.name_input.text.strip()
        surname = self.ids.surname_input.text.strip()
        full_name = f"{name} {surname}".strip() or "Ученик"
        
        day = self.get_center_value(self.ids.d_cont)
        month = self.get_center_value(self.ids.m_cont)
        year = self.get_center_value(self.ids.y_cont)
        
        # ИСПРАВЛЕНО: Создаем правильную строку прогресса для всех уровней сразу
        # Формат: "Уровень:Звезды|Уровень:Звезды|Уровень:Звезды"
        initial_progress = "1:0|1:0|1:0"
        
        # Сохраняем все 7 параметров
        save_all_data(full_name, "None", False, day, month, year, initial_progress)
        
        self.manager.current = 'menu'
class MenuScreen(Screen):
    bg_texture = get_triple_gradient()

    def set_difficulty(self, level_name):
        # 1. Загружаем ВСЕ текущие данные (ТЕПЕРЬ 7 параметров)
        # Добавляем progress в конце
        name, _, night, day, month, year, progress = load_all_data()

        # 2. Сохраняем данные обратно, обновляя ТОЛЬКО уровень
        # Обязательно передаем progress седьмым аргументом
        save_all_data(name, level_name, night, day, month, year, progress)
        
        print(f"Выбран уровень: {level_name}")
        
        # 3. Переходим в главный дашборд
        self.manager.current = 'main_dashboard'
class MainDashboard(Screen):
    bg_texture = get_triple_gradient()
    user_name_display = StringProperty("ГОСТЬ") 

    def on_enter(self):
        # Теперь принимаем 7 параметров. Седьмой (прогресс) просто помечаем как _
        name, level, night, d, m, year, _ = load_all_data()
        
        print(f"DEBUG: На главном экране имя: '{name}', уровень: '{level}'") 
        self.user_name_display = self.format_name(name)

    def format_name(self, name):
        # Разбиваем строку по пробелам (Имя Фамилия)
        parts = name.split()
        
        if len(parts) >= 2:
            # Делаем "ИВАН И."
            return f"{parts[0].upper()} {parts[1][0].upper()}."
        else:
            # Если только одно слово — просто в верхний регистр
            return name.upper()
# --- ВСТАВИТЬ ПОСЛЕ MainDashboard ---
class GrammarScreen(Screen):
    bg_texture = get_triple_gradient()
    grammar_text = StringProperty("Загрузка...")
    level_title = StringProperty("ГРАММАТИКА")

    def on_pre_enter(self):
        # ИСПРАВЛЕНО: принимаем 6 значений
        # ТЕПЕРЬ ПРИНИМАЕМ 7 ЗНАЧЕНИЙ (добавили , _)
        name, user_level, night, d, m, year, _ = load_all_data()

        file_map = {
            "Easy": ("grammar_easy.txt", "ЛЕГКИЙ УРОВЕНЬ"),
            "Medium": ("grammar_medium.txt", "СРЕДНИЙ УРОВЕНЬ"),
            "Hard": ("grammar_hard.txt", "ТРУДНЫЙ УРОВЕНЬ")
        }
        
        file_name, title = file_map.get(user_level, ("grammar_easy.txt", "ГРАММАТИКА"))
        self.level_title = title

        try:
            with open(file_name, "r", encoding='utf-8') as f:
                self.grammar_text = f.read()
        except Exception as e:
            print(f"Ошибка загрузки текста: {e}")
            self.grammar_text = f"Файл {file_name} не найден!"
class SettingsScreen(Screen):
    bg_texture = ObjectProperty(None)

    def on_pre_enter(self):
        # Обновляем фон при входе
        self.bg_texture = get_triple_gradient()

    def toggle_setting(self, setting_name, state):
        """
        Метод для переключения настроек. 
        Если это ночной режим — вызываем функцию из главного класса приложения.
        """
        app = App.get_running_app()
        
        if setting_name == "night_mode":
            # Вызываем нашу умную функцию переключения (она уже умеет сохранять 4 параметра)
            app.toggle_night_mode()
            print(f"Ночной режим изменен на: {app.dark_mode}")
        
        # Здесь можно добавить другие настройки (звук, уведомления и т.д.)
        else:
            print(f"Настройка {setting_name} теперь: {state}")
class ProfileScreen(Screen):
    bg_texture = ObjectProperty(None)
    user_full_name = StringProperty("")
    user_level_status = StringProperty("")
    user_birth_year = StringProperty("")

    def on_pre_enter(self):
        self.bg_texture = get_triple_gradient()
        # Принимаем 7 значений (добавили , progress)
        name, level, night, d, m, year, progress = load_all_data() 
        self.user_full_name = name.upper()
        self.user_level_status = f"УРОВЕНЬ: {level.upper()}"
        self.user_birth_year = f"ДАТА РОЖДЕНИЯ: {d} {m} {year}"

        # Определяем цвет текста для барабанов (белый для ночи, черный для дня)
        app = App.get_running_app()
        text_color = (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)

        # Очищаем и заполняем заново, чтобы обновить цвета
        self.ids.d_cont.clear_widgets()
        for i in range(1, 32):
            self.ids.d_cont.add_widget(Label(text=str(i), size_hint_y=None, height=40, color=text_color))
        
        self.ids.m_cont.clear_widgets()
        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        for mon in months:
            self.ids.m_cont.add_widget(Label(text=mon, size_hint_y=None, height=40, color=text_color))
        
        self.ids.y_cont.clear_widgets()
        for y in range(2026, 1949, -1):
            self.ids.y_cont.add_widget(Label(text=str(y), size_hint_y=None, height=40, color=text_color))

    def get_center_value(self, container):
        if not container.children: return "1"
        sv = container.parent
        kids = container.children[::-1] 
        idx = int((1 - max(0, min(1, sv.scroll_y))) * (len(kids) - 1))
        return kids[max(0, min(idx, len(kids)-1))].text

    def update_level(self, new_level):
        # Загружаем 7 параметров
        name, _, night, d, m, year, progress = load_all_data()
        # Сохраняем 7 параметров
        save_all_data(name, new_level, night, d, m, year, progress)
        self.user_level_status = f"УРОВЕНЬ: {new_level.upper()}"

    def update_profile_data(self):
        try:
            new_name = self.ids.name_input.text.strip()
            new_d = self.get_center_value(self.ids.d_cont)
            new_m = self.get_center_value(self.ids.m_cont)
            new_y = self.get_center_value(self.ids.y_cont)
            
            # Загружаем 7 значений
            name, level, night, d, m, year, progress = load_all_data()
            
            final_name = new_name if new_name else name
            
            # Сохраняем все 7 ПАРАМЕТРОВ
            save_all_data(final_name, level, night, new_d, new_m, new_y, progress)
            
            # Обновляем интерфейс
            self.user_full_name = final_name.upper()
            self.user_birth_year = f"ДАТА РОЖДЕНИЯ: {new_d} {new_m} {new_y}"
            self.ids.name_input.text = ""
            print("Профиль успешно обновлен")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")



# Красивая кнопка без стандартных эффектов Kivy (белых квадратов)
from kivy.uix.gridlayout import GridLayout

# Чистая кнопка без белых квадратов
class ImageButton(ButtonBehavior, Image):
    def on_press(self):
        Animation(opacity=0.6, duration=0.1).start(self)

    def on_release(self):
        Animation(opacity=1.0, duration=0.1).start(self)


class RoadmapStep(FloatLayout):
    def __init__(self, task_number, side, locked, stars_count=0, is_last=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = 1  # Растягиваем на всю ширину
        self.size_hint_y = None
        self.height = 250     # Расстояние между точками
        img_dir = 'assets/images'

        # 1. ФОТО-ЛИНИЯ (Растягивается до следующей точки)
        if not is_last:
            # Создаем изображение линии
            line_img = Image(
                source=os.path.join(img_dir, 'line.jpg'),
                allow_stretch=True,   # Разрешаем растягивание
                keep_ratio=False,     # Не сохраняем пропорции (чтобы тянулась в длину)
                size_hint=(None, None),
                width=10,             # Укажи нужную ширину линии (например, 10 пикселей)
                height=self.height,    # Растягиваем на всю высоту шага
                # 'center_x': 0.5 — в центре экрана
                # 'top': 0.5 — верх края линии совпадает с центром текущей точки
                pos_hint={'center_x': 0.5, 'top': 0.5} 
            )
            self.add_widget(line_img)

        # 2. ТОЧКА ПУТИ (Строго по центру)
        self.add_widget(Image(
            source=os.path.join(img_dir, 'point.jpg'),
            size_hint=(None, None), 
            size=(35, 35),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        ))

        # 3. КАРТОЧКА ЗАДАНИЯ
        card_x = 0.25 if side == "left" else 0.75
        task_container = FloatLayout(
            size_hint=(0.35, 0.6), 
            pos_hint={'center_x': card_x, 'center_y': 0.5}
        )

        with task_container.canvas.before:
            Color(0.5, 0.8, 1, 0.2)
            self.border = Line(rounded_rectangle=[0, 0, 0, 0, 15], width=1.5)

        def update_border(ins, val):
            self.border.rounded_rectangle = [ins.x, ins.y, ins.width, ins.height, 15]
        task_container.bind(pos=update_border, size=update_border)

        # Кнопка/Иконка
        icon_file = 'task_locked.jpg' if locked else 'task_open.jpg'
        btn = ImageButton(
            source=os.path.join(img_dir, icon_file),
            size_hint=(0.8, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        if not locked:
            btn.bind(on_release=lambda x, tn=task_number: self.start_task(tn))
            task_container.add_widget(Label(
                text=str(task_number), font_size='22sp', bold=True,
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            ))

        task_container.add_widget(btn)

        # Звезды
        stars_box = BoxLayout(
            size_hint=(None, None), size=(80, 25),
            pos_hint={'center_x': 0.5, 'y': -0.15},
            spacing=3
        )
        for i in range(1, 4):
            s_file = 'star_on.png' if i <= stars_count else 'star_off.jpg'
            stars_box.add_widget(Image(source=os.path.join(img_dir, s_file)))
        
        task_container.add_widget(stars_box)
        self.add_widget(task_container)

    def start_task(self, num):
        from kivy.app import App
        app = App.get_running_app()
        sn = f"ex_{num}"
        if not app.root.has_screen(sn):
            from final import ExerciseScreen
            app.root.add_widget(ExerciseScreen(name=sn, exercise_id=str(num)))
        app.root.current = sn




class LevelMapScreen(Screen):
    level_title = StringProperty("УРОВЕНЬ")
    bg_texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.bg_texture = get_triple_gradient()
        except Exception as e:
            print(f"Ошибка создания текстуры: {e}")

    def on_enter(self, *args):
        Clock.schedule_once(self.build_roadmap, 0.1)

    def build_roadmap(self, dt=None):
        if 'map_container' not in self.ids: return
        container = self.ids.map_container
        container.clear_widgets()
        container.bind(minimum_height=container.setter('height'))

        app = App.get_running_app()
        try:
            res = load_all_data()
            name, level, night, d, m, y, progress_str = res
        except Exception as e:
            progress_str = "1-0|1-0|1-0"
            level = "Easy"

        current_lvl = str(level) if (level and str(level) != "None") else "Easy"
        from game_logic import get_menu_data
        config = get_menu_data(current_lvl)
        self.level_title = config.get("title", "УРОВЕНЬ")
        
        # --- НОВАЯ ЛОГИКА ПРОГРЕССА (ID-STARS) ---
        # Создаем словарь текущего прогресса {номер_уровня: звезды}
        progress_dict = {}
        max_opened = 1
        
        try:
            parts = progress_str.split('|')
            idx = 0 if current_lvl == "Easy" else 1 if current_lvl == "Medium" else 2
            
            # Разбиваем часть сложности (например, "1-3,2-0")
            levels_data = parts[idx].split(',')
            for item in levels_data:
                if '-' in item:
                    lv_id, lv_stars = map(int, item.split('-'))
                    progress_dict[lv_id] = lv_stars
                    if lv_id > max_opened:
                        max_opened = lv_id
        except Exception as e:
            print(f"Ошибка разбора прогресса: {e}")
            max_opened = 1
        
        tasks_count = config.get("tasks_count", 7)

        for i in range(1, tasks_count + 1):
            side = "left" if i % 2 != 0 else "right"
            
            # Уровень закрыт, если его нет в списке прогресса
            is_locked = i not in progress_dict
            
            # Звезды берем персонально для каждого ID из нашего словаря
            stars_to_show = progress_dict.get(i, 0)

            step = RoadmapStep(
                task_number=i, 
                side=side, 
                locked=is_locked,
                stars_count=stars_to_show, 
                is_last=(i == tasks_count)
            )
            container.add_widget(step)

        # Кнопка перехода на след. этап (если все задачи пройдены)
        if max_opened > tasks_count:
            next_btn_area = BoxLayout(size_hint_y=None, height=150, padding=40)
            btn = Button(
                text="ОТКРЫТЬ СЛЕДУЮЩИЙ ЭТАП",
                background_normal='',
                background_color=(0.1, 0.5, 0.9, 1),
                bold=True, font_size='18sp'
            )
            btn.bind(on_release=self.go_next_level)
            next_btn_area.add_widget(btn)
            container.add_widget(next_btn_area)

    def go_next_level(self, instance):
        app = App.get_running_app()
        if app.user_level == "Easy":
            app.user_level = "Medium"
        elif app.user_level == "Medium":
            app.user_level = "Hard"
        
        # Обнуляем прогресс для новой сложности, если там еще пусто
        # Это вызовет сохранение в новом формате
        self.build_roadmap()




class ExerciseScreen(Screen):
    display_mode = StringProperty("lesson")
    image_source = StringProperty("")
    question_text = StringProperty("")
    grammar_hint = StringProperty("")
    options = ListProperty(["", "", "", ""])
    current_part = NumericProperty(1)
    exercise_id = StringProperty("1")
    # Инициализируем DictProperty для отслеживания изменений в KV
    step_results = DictProperty({"1": None, "2": None, "3": None, "4": None, "5": None})
    correct_answer = ""

    def on_pre_enter(self):
        """ Очистка перед входом на экран """
        self.current_part = 1
        self.step_results = {"1": None, "2": None, "3": None, "4": None, "5": None}
        if hasattr(self.ids, 'ans_input'):
            self.ids.ans_input.text = ""
        self.load_initial_data()

    def show_step_help(self):
        """ Метод для показа фото-подсказки из папки уровня """
        from kivy.uix.popup import Popup
        from kivy.uix.image import Image as KivyImage
        import os

        app = App.get_running_app()
        
        # Получаем сложность (easy, medium, hard) и переводим в нижний регистр
        lvl_folder = app.user_level.lower() 
        
        # Получаем номер упражнения
        current_id = self.exercise_id if self.exercise_id else "1"

        # Собираем путь: assets/levels/easy/1_help.jpg
        # Если расширение файла другое (например, .png), замени его ниже
        path_to_help = f"assets/levels/{lvl_folder}/{current_id}_help.jpg"

        if os.path.exists(path_to_help):
            content = KivyImage(
                source=path_to_help,
                allow_stretch=True,
                keep_ratio=True
            )
        else:
            # Если фото не найдено, выведем текст с путем, чтобы ты мог проверить
            from kivy.uix.label import Label
            content = Label(
                text=f"Файл не найден:\n{path_to_help}",
                halign='center'
            )

        popup = Popup(
            title=f'ПОМОЩЬ: УРОВЕНЬ {current_id}',
            content=content,
            size_hint=(0.9, 0.8)
        )
        popup.open()

    def load_initial_data(self):
        from game_logic import get_exercise_data
        app = App.get_running_app()
        
        if not self.exercise_id:
            self.exercise_id = "1"

        data = get_exercise_data(app.user_level, str(self.exercise_id), "1")
        
        if not data:
            self.manager.current = 'level_map'
            return

        self.display_mode = data.get("type", "rebus")
        
        if self.display_mode == "dictation":
            raw_text = data.get("full_text") or data.get("text")
            self.question_text = raw_text if raw_text else "Текст отсутствует"
            self.image_source = ""
        
        self.load_step_logic(self.current_part)

    def load_step_logic(self, step):
        from game_logic import get_exercise_data
        app = App.get_running_app()
        data = get_exercise_data(app.user_level, str(self.exercise_id), str(step))
        
        if data:
            self.correct_answer = str(data.get("ans", "")).strip().lower()
            self.grammar_hint = data.get("hint", "")
            
            if self.display_mode in ["rebus", "lesson"]:
                img_name = data.get("img", "")
                if img_name:
                    lvl_folder = app.user_level.lower()
                    self.image_source = f"assets/levels/{lvl_folder}/{img_name}"
                else:
                    self.image_source = ""
                self.question_text = "" 

    def on_ref_press(self, instance, ref):
        try:
            self.current_part = int(ref)
            self.load_step_logic(self.current_part)
            if hasattr(self.ids, 'ans_input'):
                self.ids.ans_input.focus = True
                self.ids.ans_input.text = ""
        except: 
            pass

    def check_answer(self, user_val=None):
        new_results = dict(self.step_results)
        
        if self.display_mode == "lesson":
            new_results[str(self.current_part)] = True
            self.step_results = new_results
            self.next_step()
            return

        ans = ""
        if user_val is not None:
            ans = str(user_val).strip().lower()
        elif hasattr(self.ids, 'ans_input'):
            ans = self.ids.ans_input.text.strip().lower()

        is_correct = (ans == self.correct_answer)
        new_results[str(self.current_part)] = is_correct
        self.step_results = new_results
        
        if hasattr(self.ids, 'ans_input'):
            self.ids.ans_input.text = ""
        
        self.next_step()

    def next_step(self):
        max_parts = 5
        if self.display_mode == "dictation":
            answered_count = sum(1 for v in self.step_results.values() if v is not None)
            if answered_count >= max_parts:
                self.complete_exercise()
            else:
                for i in range(1, max_parts + 1):
                    if self.step_results[str(i)] is None:
                        self.on_ref_press(None, str(i))
                        break
        else:
            if self.current_part < max_parts:
                self.current_part += 1
                self.load_step_logic(self.current_part)
            else:
                self.complete_exercise()

    def complete_exercise(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.image import Image as KivyImage
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.popup import Popup

        correct_count = sum(1 for res in self.step_results.values() if res is True)
        stars = 3 if correct_count == 5 else 2 if correct_count >= 3 else 1 if correct_count >= 1 else 0
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        stars_img = f'assets/images/star_{stars}.png'
        if os.path.exists(stars_img):
            content.add_widget(KivyImage(source=stars_img, size_hint_y=2))
        
        content.add_widget(Label(text=f"Правильно: {correct_count} из 5", font_size='20sp', bold=True))
        btn = Button(text="ЗАКОНЧИТЬ", size_hint_y=None, height=50, background_color=(0.2, 0.7, 0.3, 1))
        content.add_widget(btn)

        popup = Popup(title='Упражнение завершено', content=content, size_hint=(0.8, 0.5), auto_dismiss=False)
        btn.bind(on_release=lambda x: [popup.dismiss(), self.finish_and_save(correct_count)])
        popup.open()

    def finish_and_save(self, correct_count):
        from game_logic import save_all_data, load_all_data
        app = App.get_running_app()
        res = load_all_data()
        stars = 3 if correct_count == 5 else 2 if correct_count >= 3 else 1 if correct_count >= 1 else 0
        if res and len(res) >= 7:
            name, level, night, d, m, y, progress_str = res
            parts = progress_str.split('|')
            idx = 0 if level == "Easy" else 1 if level == "Medium" else 2
            levels_data = parts[idx].split(',')
            progress_dict = {}
            for item in levels_data:
                if '-' in item:
                    lv_id, lv_stars = item.split('-')
                    progress_dict[lv_id] = lv_stars
            this_id = str(self.exercise_id)
            old_stars = int(progress_dict.get(this_id, 0))
            progress_dict[this_id] = str(max(old_stars, stars))
            next_id = str(int(this_id) + 1)
            if next_id not in progress_dict:
                progress_dict[next_id] = "0"
            parts[idx] = ",".join([f"{k}-{v}" for k, v in progress_dict.items()])
            new_prog = "|".join(parts)
            save_all_data(name, level, night, d, m, y, new_prog)
            app.user_progress = new_prog
        self.manager.current = 'level_map'

    def go_back(self):
        self.manager.current = 'level_map'
class AboutScreen(Screen):
    bg_texture = ObjectProperty(None)
    
    # ЗАМЕНИ ЭТОТ ТЕКСТ:
    about_text = StringProperty(
        "[b]НАУЧНЫЙ ПРОЕКТ[/b]\n"
        "Интерактивный тренажер по орфографии\n"
        "«Орфо-драйв»\n\n"
        "[b]1. Авторы:[/b]\nАлламырадова Джемал, Нурлыев Аманмырат, Чарыев Безирген\n\n"
        "[b]2. Название проекта:[/b]\nИнтерактивный тренажер «Орфо-драйв»\n\n"
        "[b]3. Вид проекта:[/b]\nИнформационно-образовательная программа\n\n"
        "[b]4. Описание:[/b]\nТренажер представляет собой цифровую среду, где изучение орфограмм происходит через разгадывание ребусов. Программа включает разделы по самым сложным темам правописания.\n\n"
        "[b]5. Предмет проекта:[/b]\nРазработка и внедрение интерактивных форм контроля и самоконтроля знаний по русскому языку.\n\n"
        "[b]Идея проекта:[/b]\nИспользование методов геймификации для повышения эффективности освоения языка. Каждая орфограмма зашифрована в уникальном визуальном ребусе."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_texture = get_triple_gradient()
    def on_pre_enter(self):
        # Обновляем фон при входе, если это нужно для анимации
        self.bg_texture = get_triple_gradient()
class HelpScreen(Screen):
    bg_texture = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Эта строчка рисует твой сине-белый фон
        self.bg_texture = get_triple_gradient()
    pass
class FixedWheel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Скрываем полоски прокрутки для чистого вида барабана
        self.bar_width = 0
        self.scroll_type = ['content']
class RussianApp(App):
    # Свойства приложения с правильными начальными значениями
    dark_mode = BooleanProperty(False)
    user_name = StringProperty("Ученик")
    user_level = StringProperty("Easy")  # По умолчанию Easy, а не None
    user_day = StringProperty("1")
    user_month = StringProperty("Янв")
    user_year = StringProperty("2026")
    user_progress = StringProperty("1:0|1:0|1:0") 

    def build(self):
        from game_logic import load_all_data
        
        # 1. Загрузка данных
        try:
            res = load_all_data()
            if len(res) == 7:
                # Распаковываем данные
                self.user_name = str(res[0])
                self.user_level = str(res[1])
                
                # Исправляем Boolean: если в файле "True", "1" или True — будет True
                dm = res[2]
                self.dark_mode = True if str(dm).lower() in ["true", "1", "yes"] else False
                
                self.user_day = str(res[3])
                self.user_month = str(res[4])
                self.user_year = str(res[5])
                self.user_progress = str(res[6])
                
                print(f"Данные загружены: {self.user_level}, Progress: {self.user_progress}")
        except Exception as e:
            print(f"Ошибка загрузки данных при старте: {e}")

        # 2. Создаем менеджер экранов
        sm = ScreenManager(transition=FadeTransition(duration=0.4))
        
        # Список классов экранов (проверь, чтобы названия exercise_screen совпали с картой)
        screen_classes = [
            (SplashScreen, 'splash'),
            (RegisterScreen, 'register'),
            (MenuScreen, 'menu'),
            (MainDashboard, 'main_dashboard'),
            (LevelMapScreen, 'level_map'),
            (GrammarScreen, 'grammar_view'),
            (ExerciseScreen, 'exercise'), # Убедись, что на карте вызывается 'exercise'
            (ProfileScreen, 'profile_screen'),
            (SettingsScreen, 'settings'),
            (AboutScreen, 'about_screen'),
            (HelpScreen, 'help_screen')
        ]
        
        # Безопасно добавляем экраны
        for cls, name in screen_classes:
            try:
                sm.add_widget(cls(name=name))
            except Exception as e:
                print(f"Ошибка в экране '{name}': {e}")
                dummy = Screen(name=name)
                dummy.add_widget(Label(text=f"Ошибка в {name}", color=(1,0,0,1)))
                sm.add_widget(dummy)

        return sm

    def toggle_night_mode(self, *args):
        """Переключение темы с сохранением"""
        from game_logic import save_all_data
        try:
            self.dark_mode = not self.dark_mode
            
            # Сохраняем всё как строки для стабильности
            save_all_data(
                str(self.user_name), 
                str(self.user_level), 
                "True" if self.dark_mode else "False", 
                str(self.user_day), 
                str(self.user_month), 
                str(self.user_year), 
                str(self.user_progress)
            )
        except Exception as e:
            print(f"Ошибка при смене темы: {e}")

if __name__ == '__main__':
    RussianApp().run()











