from kivy.uix.screenmanager import ScreenManager, Screen 
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from datetime import datetime
from kivy.core.window import Window

# Importações necessárias para a aba customizada
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.tab import MDTabsBase

Window.size = (350, 600)

# Classe customizada para as abas
class MyTab(BoxLayout, MDTabsBase):
    pass

class DialogContent(MDBoxLayout):
    # Declaramos as propriedades para que o KV as reconheça
    selected_date = StringProperty()
    selected_time = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Define os valores padrões para data e horário
        self.selected_date = datetime.now().strftime('%d/%m/%Y')
        self.selected_time = datetime.now().strftime('%H:%M')

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.selected_date = value.strftime('%d/%m/%Y')
        self.ids.date_label.text = f"Data: {self.selected_date}"

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.on_time_save)
        time_dialog.open()

    def on_time_save(self, instance, time_obj):
        self.selected_time = time_obj.strftime("%H:%M")
        self.ids.time_label.text = f"Horário: {self.selected_time}"

class ToDoCard(MDBoxLayout):
    title = StringProperty()
    description = StringProperty()
    date = StringProperty()
    time = StringProperty()
    completed = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True

class ToDoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Lista que armazenará as tarefas (cada tarefa é um dicionário)
        self.tasks = []
        self.dialog = None  # Diálogo para criação de tarefas (para evitar recriação)

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        return Builder.load_file('todo.kv')

    def show_task_dialog(self):
        if not self.dialog:
            self.dialog_content = DialogContent()
            self.dialog = MDDialog(
                title="Nova Tarefa",
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="ADICIONAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=lambda x: self._add_task_from_dialog()
                    ),
                ],
            )
        self.dialog.open()

    def _add_task_from_dialog(self):
        title = self.dialog_content.ids.title_input.text
        description = self.dialog_content.ids.description_input.text or ""
        date = self.dialog_content.selected_date
        time = self.dialog_content.selected_time

        if title.strip():
            # Adiciona a nova tarefa (incluindo o horário)
            self.tasks.append({
                'title': title,
                'description': description,
                'date': date,
                'time': time,
                'completed': False
            })
            self.update_tasks()
            self.dialog.dismiss()
            self.dialog_content.ids.title_input.text = ""
            self.dialog_content.ids.description_input.text = ""

    def on_complete(self, checkbox, value, task_item):
        try:
            idx = self.tasks.index(task_item)
            self.tasks[idx]['completed'] = value
        except ValueError:
            pass
        self.update_tasks()

    def delete_task(self, instance, task_item):
        try:
            self.tasks.remove(task_item)
        except ValueError:
            pass
        self.update_tasks()

    def update_tasks(self):
        pending_container = self.root.ids.pending_tasks_container
        completed_container = self.root.ids.completed_tasks_container

        pending_container.clear_widgets()
        completed_container.clear_widgets()

        # Ordena as tarefas pendentes e concluídas por data e horário
        def sort_key(task):
            dt_str = f"{task['date']} {task['time']}"
            return datetime.strptime(dt_str, '%d/%m/%Y %H:%M')

        pending_tasks = sorted(
            [task for task in self.tasks if not task['completed']],
            key=sort_key
        )
        completed_tasks = sorted(
            [task for task in self.tasks if task['completed']],
            key=sort_key
        )

        # Cria os cards para as tarefas pendentes
        for task in pending_tasks:
            card = ToDoCard(
                title=task['title'],
                description=task['description'],
                date=task['date'],
                time=task['time'],
                completed=task['completed']
            )
            card.ids.checkbox.bind(
                active=lambda cb, value, task_item=task: self.on_complete(cb, value, task_item)
            )
            card.ids.delete_button.bind(
                on_release=lambda btn, task_item=task: self.delete_task(btn, task_item)
            )
            pending_container.add_widget(card)

        # Cria os cards para as tarefas concluídas
        for task in completed_tasks:
            card = ToDoCard(
                title=task['title'],
                description=task['description'],
                date=task['date'],
                time=task['time'],
                completed=task['completed']
            )
            card.ids.checkbox.bind(
                active=lambda cb, value, task_item=task: self.on_complete(cb, value, task_item)
            )
            card.ids.delete_button.bind(
                on_release=lambda btn, task_item=task: self.delete_task(btn, task_item)
            )
            completed_container.add_widget(card)

if __name__ == '__main__':
    ToDoApp().run()