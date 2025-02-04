from kivy.uix.screenmanager import ScreenManager, Screen 
from kivymd.app import MDApp
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

# Classe customizada para as abas (usada no MDTabs)
class MyTab(BoxLayout, MDTabsBase):
    pass

class DialogContent(MDBoxLayout):
    # Propriedades para que o KV as reconheça
    selected_date = StringProperty()
    selected_time = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Valores padrão para data e horário
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
        # Lista que armazena as tarefas (cada tarefa é um dicionário)
        self.tasks = []
        self.dialog = None         # Diálogo para criar/editar tarefas
        self.delete_dialog = None  # Diálogo de confirmação para exclusão
        self.task_to_edit = None   # Tarefa atualmente em edição (se houver)
        self.revert_dialog = None  # Diálogo de confirmação para reverter tarefa

    # Não chamamos explicitamente Builder.load_file() pois o KivyMD carrega automaticamente
    # o arquivo KV seguindo a convenção de nomenclatura.

    def show_task_dialog(self, edit_task=None):
        """
        Abre o diálogo para criar ou editar tarefa.
        Se edit_task for fornecida, os campos são pré-preenchidos.
        """
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
                        text="SALVAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=lambda x: self._save_task()
                    ),
                ],
            )
        if edit_task:
            self.task_to_edit = edit_task
            self.dialog.title = "Editar Tarefa"
            self.dialog_content.ids.title_input.text = edit_task['title']
            self.dialog_content.ids.description_input.text = edit_task['description']
            self.dialog_content.selected_date = edit_task['date']
            self.dialog_content.selected_time = edit_task['time']
            self.dialog_content.ids.date_label.text = f"Data: {edit_task['date']}"
            self.dialog_content.ids.time_label.text = f"Horário: {edit_task['time']}"
        else:
            self.task_to_edit = None
            self.dialog.title = "Nova Tarefa"
            self.dialog_content.ids.title_input.text = ""
            self.dialog_content.ids.description_input.text = ""
            self.dialog_content.selected_date = datetime.now().strftime('%d/%m/%Y')
            self.dialog_content.selected_time = datetime.now().strftime('%H:%M')
            self.dialog_content.ids.date_label.text = f"Data: {self.dialog_content.selected_date}"
            self.dialog_content.ids.time_label.text = f"Horário: {self.dialog_content.selected_time}"
        self.dialog.open()

    def _save_task(self):
        title = self.dialog_content.ids.title_input.text
        description = self.dialog_content.ids.description_input.text or ""
        date = self.dialog_content.selected_date
        time = self.dialog_content.selected_time

        if title.strip():
            if self.task_to_edit:
                idx = self.tasks.index(self.task_to_edit)
                self.tasks[idx]['title'] = title
                self.tasks[idx]['description'] = description
                self.tasks[idx]['date'] = date
                self.tasks[idx]['time'] = time
            else:
                self.tasks.append({
                    'title': title,
                    'description': description,
                    'date': date,
                    'time': time,
                    'completed': False
                })
            self.update_tasks()
            self.dialog.dismiss()

    def on_complete(self, checkbox, value, task_item):
        try:
            idx = self.tasks.index(task_item)
            self.tasks[idx]['completed'] = value
        except ValueError:
            pass
        self.update_tasks()

    def delete_task(self, instance, task_item):
        # Exibe caixa de diálogo para confirmar exclusão
        self.task_to_delete = task_item
        self.delete_dialog = MDDialog(
            title="Confirmar Exclusão",
            text="Você realmente deseja excluir esta tarefa?",
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.delete_dialog.dismiss()
                ),
                MDFlatButton(
                    text="EXCLUIR",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self._confirm_delete()
                ),
            ]
        )
        self.delete_dialog.open()

    def _confirm_delete(self):
        try:
            self.tasks.remove(self.task_to_delete)
        except ValueError:
            pass
        self.update_tasks()
        self.delete_dialog.dismiss()

    def revert_task(self, instance, task_item):
        # Exibe caixa de diálogo para confirmar a reversão da tarefa
        self.task_to_revert = task_item
        self.revert_dialog = MDDialog(
            title="Desfazer conclusão",
            text="Deseja desfazer a conclusão desta tarefa?",
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.revert_dialog.dismiss()
                ),
                MDFlatButton(
                    text="CONFIRMAR",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self._confirm_revert()
                ),
            ]
        )
        self.revert_dialog.open()

    def _confirm_revert(self):
        try:
            idx = self.tasks.index(self.task_to_revert)
            self.tasks[idx]['completed'] = False
        except ValueError:
            pass
        self.update_tasks()
        self.revert_dialog.dismiss()

    def update_tasks(self):
        pending_container = self.root.ids.pending_tasks_container
        completed_container = self.root.ids.completed_tasks_container

        pending_container.clear_widgets()
        completed_container.clear_widgets()

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
            card.ids.edit_button.bind(
                on_release=lambda btn, task_item=task: self.show_task_dialog(edit_task=task_item)
            )
            pending_container.add_widget(card)

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
            card.ids.edit_button.bind(
                on_release=lambda btn, task_item=task: self.show_task_dialog(edit_task=task_item)
            )
            # Vincula o novo botão de reverter (aparece somente em tarefas concluídas)
            card.ids.revert_button.bind(
                on_release=lambda btn, task_item=task: self.revert_task(btn, task_item)
            )
            completed_container.add_widget(card)

if __name__ == '__main__':
    ToDoApp().run()
