from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime

Window.size = (350, 600)

class DialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_date = datetime.now().strftime('%d/%m/%Y')

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        self.selected_date = value.strftime('%d/%m/%Y')
        self.ids.date_label.text = f"Data: {self.selected_date}"

class ToDoCard(MDBoxLayout):
    title = StringProperty()
    description = StringProperty()
    date = StringProperty()
    completed = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True

class ToDoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []
        self.dialog = None  # Armazena o diálogo para evitar recriação

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        return Builder.load_file('todo.kv')

    def show_task_dialog(self):
        if not self.dialog:  # Cria o diálogo apenas se ainda não existir
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
        
        if title.strip():
            self.tasks.append({
                'title': title,
                'description': description,
                'date': date,
                'completed': False
            })
            self.update_tasks()
            self.dialog.dismiss()
            self.dialog_content.ids.title_input.text = ""
            self.dialog_content.ids.description_input.text = ""

    def on_complete(self, checkbox, value, task_index):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]['completed'] = value

    def delete_task(self, task_index):
        if 0 <= task_index < len(self.tasks):
            self.tasks.pop(task_index)
            self.update_tasks()

    def update_tasks(self):
        container = self.root.ids.task_container
        container.clear_widgets()
        
        for index, task in enumerate(self.tasks):
            card = ToDoCard(
                title=task['title'],
                description=task['description'],
                date=task['date'],
                completed=task['completed']
            )
            
            card.ids.checkbox.bind(
                active=lambda cb, value, idx=index: self.on_complete(cb, value, idx)
            )
            card.ids.delete_button.bind(
                on_release=lambda btn, idx=index: self.delete_task(idx)
            )
            
            container.add_widget(card)

if __name__ == '__main__':
    ToDoApp().run()
