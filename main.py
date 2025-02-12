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

# --------------------------
# TELAS
# --------------------------

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class MainScreen(Screen):
    pass

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
        # Define a data mínima como a data atual para bloquear datas anteriores
        date_dialog = MDDatePicker(min_date=datetime.now().date())
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        # Converte a data selecionada para um objeto date
        selected = value if hasattr(value, "year") else datetime.now().date()
        if selected < datetime.now().date():
            error_dialog = MDDialog(
                title="Data Inválida",
                text="Não é permitido selecionar uma data anterior à data atual.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return  # Não atualiza a data se for inválida
        self.selected_date = selected.strftime('%d/%m/%Y')
        self.ids.date_label.text = f"Data: {self.selected_date}"

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.on_time_save)
        time_dialog.open()

    def on_time_save(self, instance, time_obj):
        # Se o objeto retornado não tiver o método strftime (por exemplo, ao selecionar a hora 0), define manualmente
        if not hasattr(time_obj, "strftime"):
            self.selected_time = "00:00"
        else:
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

# --------------------------
# APLICATIVO
# --------------------------
class ToDoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Lista que armazena as tarefas (cada tarefa é um dicionário)
        self.tasks = []
        self.dialog = None         # Diálogo para criar/editar tarefas
        self.delete_dialog = None  # Diálogo de confirmação para exclusão
        self.task_to_edit = None   # Tarefa atualmente em edição (se houver)
        self.revert_dialog = None  # Diálogo de confirmação para reverter tarefa

        # Variáveis para armazenar credenciais do usuário cadastrado
        self.registered_username = None
        self.registered_password = None

    def build(self):
        # O arquivo KV será carregado automaticamente
        return self.root

    # --------------------------
    # MÉTODOS DE LOGIN E CADASTRO
    # --------------------------
    def do_login(self, username, password):
        # Verifica se há um usuário cadastrado
        if not self.registered_username or not self.registered_password:
            error_dialog = MDDialog(
                title="Erro de Login",
                text="Nenhum usuário cadastrado. Cadastre um usuário antes de fazer login.",
                buttons=[
                    MDFlatButton(
                        text="OK", 
                        theme_text_color="Custom", 
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return

        # Verifica se as credenciais conferem
        if username == self.registered_username and password == self.registered_password:
            self.root.current = "main"  # Troca para a tela principal
        else:
            error_dialog = MDDialog(
                title="Erro de Login",
                text="Usuário ou senha incorretos.",
                buttons=[
                    MDFlatButton(
                        text="OK", 
                        theme_text_color="Custom", 
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def do_register(self):
        # Navega para a tela de cadastro
        self.root.current = "register"

    def register_user(self, username, password):
        if not username.strip() or not password.strip():
            error_dialog = MDDialog(
                title="Erro no Cadastro",
                text="Nome de usuário e senha são obrigatórios.",
                buttons=[
                    MDFlatButton(
                        text="OK", 
                        theme_text_color="Custom", 
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return

        self.registered_username = username
        self.registered_password = password

        success_dialog = MDDialog(
            title="Sucesso",
            text="Cadastro realizado com sucesso.",
            buttons=[
                MDFlatButton(
                    text="OK", 
                    theme_text_color="Custom", 
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: success_dialog.dismiss()
                )
            ],
        )
        # Após fechar o diálogo, volta para a tela de login
        success_dialog.bind(on_dismiss=lambda *args: self.go_to_login())
        success_dialog.open()

    def go_to_login(self):
        self.root.current = "login"

    # --------------------------
    # MÉTODOS PARA AS TAREFAS
    # --------------------------
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
        date_str = self.dialog_content.selected_date
        # Converte a string para um objeto date
        selected_date = datetime.strptime(date_str, '%d/%m/%Y').date()

        # Validação para impedir salvar datas anteriores à data atual
        if selected_date < datetime.now().date():
            error_dialog = MDDialog(
                title="Data Inválida",
                text="Não é permitido salvar uma tarefa com data anterior à data atual.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return  # Impede o salvamento da tarefa

        if title.strip():
            if self.task_to_edit:
                idx = self.tasks.index(self.task_to_edit)
                self.tasks[idx]['title'] = title
                self.tasks[idx]['description'] = description
                self.tasks[idx]['date'] = date_str
                self.tasks[idx]['time'] = self.dialog_content.selected_time
            else:
                self.tasks.append({
                    'title': title,
                    'description': description,
                    'date': date_str,
                    'time': self.dialog_content.selected_time,
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
        pending_container = self.root.get_screen("main").ids.pending_tasks_container
        completed_container = self.root.get_screen("main").ids.completed_tasks_container

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
            card.ids.revert_button.bind(
                on_release=lambda btn, task_item=task: self.revert_task(btn, task_item)
            )
            completed_container.add_widget(card)

if __name__ == '__main__':
    ToDoApp().run()
