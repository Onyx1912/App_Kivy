import pyrebase
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.properties import StringProperty, BooleanProperty, OptionProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from datetime import datetime
from kivy.core.window import Window
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.tab import MDTabsBase

# Define o tamanho da janela
Window.size = (350, 600)

# --------------------------
# Definição das TELAS
# --------------------------
class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class MainScreen(Screen):
    pass

# Aba customizada (combina BoxLayout e MDTabsBase)
class MyTab(BoxLayout, MDTabsBase):
    pass

# --------------------------
# Diálogo para criação/edição de tarefas
# --------------------------
class DialogContent(MDBoxLayout):
    selected_date = StringProperty()
    selected_time = StringProperty()
    priority = OptionProperty("medium", options=["high", "medium", "low"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_date = datetime.now().strftime('%d/%m/%Y')
        self.selected_time = datetime.now().strftime('%H:%M')
        self.menu_items = [
            {"text": MDApp.get_running_app().t("priority_high"), "viewclass": "OneLineListItem", "on_release": lambda x="high": self.set_priority(x)},
            {"text": MDApp.get_running_app().t("priority_medium"), "viewclass": "OneLineListItem", "on_release": lambda x="medium": self.set_priority(x)},
            {"text": MDApp.get_running_app().t("priority_low"), "viewclass": "OneLineListItem", "on_release": lambda x="low": self.set_priority(x)},
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.priority_dropdown,
            items=self.menu_items,
            position="auto",
            width_mult=4,
        )

    def update_menu_items(self):
        self.menu.items = [
            {"text": MDApp.get_running_app().t("priority_high"), "viewclass": "OneLineListItem", "on_release": lambda x="high": self.set_priority(x)},
            {"text": MDApp.get_running_app().t("priority_medium"), "viewclass": "OneLineListItem", "on_release": lambda x="medium": self.set_priority(x)},
            {"text": MDApp.get_running_app().t("priority_low"), "viewclass": "OneLineListItem", "on_release": lambda x="low": self.set_priority(x)},
        ]
        
    def update_fields_text(self):
        # Atualiza os textos dos campos de nome e descrição
        self.ids.title_input.hint_text = MDApp.get_running_app().t("task_name")
        self.ids.title_input.helper_text = MDApp.get_running_app().t("task_name")
        self.ids.description_input.hint_text = MDApp.get_running_app().t("task_description")

    def set_priority(self, priority):
        self.priority = priority
        self.menu.dismiss()
        label_text = MDApp.get_running_app().t("priority") + (
            MDApp.get_running_app().t("priority_high") if priority == "high"
            else (MDApp.get_running_app().t("priority_medium") if priority == "medium" else MDApp.get_running_app().t("priority_low"))
        )
        self.ids.priority_label.text = label_text

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_date=datetime.now().date())
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        selected = value if hasattr(value, "year") else datetime.now().date()
        if selected < datetime.now().date():
            error_dialog = MDDialog(
                title=MDApp.get_running_app().t("error_date_title"),
                text=MDApp.get_running_app().t("error_date_text"),
                buttons=[
                    MDFlatButton(
                        text=MDApp.get_running_app().t("cancel"),
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return
        self.selected_date = selected.strftime('%d/%m/%Y')
        self.ids.date_label.text = f"{MDApp.get_running_app().t('date')}{self.selected_date}"

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.on_time_save)
        time_dialog.open()

    def on_time_save(self, instance, time_obj):
        if not hasattr(time_obj, "strftime"):
            self.selected_time = "00:00"
        else:
            self.selected_time = time_obj.strftime("%H:%M")
        self.ids.time_label.text = f"{MDApp.get_running_app().t('time')}{self.selected_time}"

# --------------------------
# Card que representa uma tarefa
# --------------------------
class ToDoCard(MDBoxLayout):
    title = StringProperty()
    description = StringProperty()
    date = StringProperty()
    time = StringProperty()
    completed = BooleanProperty(False)
    priority = OptionProperty("medium", options=["high", "medium", "low"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True

# --------------------------
# Aplicativo Principal
# --------------------------
class ToDoApp(MDApp):
    language = StringProperty("pt")
    # Propriedades reativas para os botões de filtro
    filter_all = StringProperty()
    filter_high = StringProperty()
    filter_medium = StringProperty()
    filter_low = StringProperty()
    # Propriedades para textos principais
    main_title = StringProperty()
    filter_priority_text = StringProperty()
    pending_tasks_text = StringProperty()
    completed_tasks_text = StringProperty()

    translations = {
        "pt": {
            "login": "Login",
            "enter": "Entrar",
            "register_user": "Cadastrar Usuário",
            "error_login_title": "Erro de Login",
            "error_login_text": "Usuário ou senha incorretos.",
            "error_register_title": "Erro no Cadastro",
            "error_register_text": "Nome de usuário e senha são obrigatórios.",
            "domain_invalid_title": "Domínio Inválido",
            "domain_invalid_text": "O e-mail deve possuir o domínio @ufrpe.br.",
            "password_invalid_title": "Senha Inválida",
            "password_invalid_text": "A senha deve conter pelo menos 6 caracteres.",
            "success_title": "Sucesso",
            "success_text": "Cadastro realizado com sucesso.",
            "new_task": "Nova Tarefa",
            "edit_task": "Editar Tarefa",
            "save": "Salvar",
            "change_date": "Alterar Data",
            "change_time": "Alterar Horário",
            "select_priority": "Selecionar Prioridade",
            "date": "Data: ",
            "time": "Horário: ",
            "priority": "Prioridade: ",
            "priority_high": "Alta",
            "priority_medium": "Média",
            "priority_low": "Baixa",
            "error_date_title": "Data Inválida",
            "error_date_text": "Não é permitido selecionar uma data anterior à data atual.",
            "cancel": "CANCELAR",
            "delete": "EXCLUIR",
            "confirm": "CONFIRMAR",
            "confirm_delete_title": "Confirmar Exclusão",
            "confirm_delete_text": "Você realmente deseja excluir esta tarefa?",
            "confirm_reversion_title": "Desfazer Conclusão",
            "confirm_reversion_text": "Deseja desfazer a conclusão desta tarefa?",
            "minhas_tarefas": "Minhas Tarefas",
            "logout": "Sair",
            "filter_priority": "Filtrar por Prioridade:",
            "all": "Todas",
            "high": "Alta",
            "medium": "Média",
            "low": "Baixa",
            "register_title": "Cadastro de Usuário",
            "email": "Email",
            "password": "Senha",
            "enter_email": "Digite o seu email",
            "enter_password": "Digite a senha",
            "register_helper_email": "Digite seu email (@ufrpe.br)",
            "register_helper_password": "Digite a senha (mín. 6 caracteres)",
            "register": "Cadastrar",
            "back_to_login": "Voltar para Login",
            "pending_tasks": "Pendentes",
            "completed_tasks": "Concluídas",
            "select_language": "Selecionar Idioma",
            "choose_language_text": "Escolha seu idioma preferido:",
            "task_name": "Nome da Tarefa",
            "task_description": "Descrição (opcional)"
        },
        "en": {
            "login": "Login",
            "enter": "Enter",
            "register_user": "Register User",
            "error_login_title": "Login Error",
            "error_login_text": "Incorrect username or password.",
            "error_register_title": "Registration Error",
            "error_register_text": "Username and password are required.",
            "domain_invalid_title": "Invalid Domain",
            "domain_invalid_text": "The email must have the @ufrpe.br domain.",
            "password_invalid_title": "Invalid Password",
            "password_invalid_text": "The password must have at least 6 characters.",
            "success_title": "Success",
            "success_text": "Registration successful.",
            "new_task": "New Task",
            "edit_task": "Edit Task",
            "save": "Save",
            "change_date": "Change Date",
            "change_time": "Change Time",
            "select_priority": "Select Priority",
            "date": "Date: ",
            "time": "Time: ",
            "priority": "Priority: ",
            "priority_high": "High",
            "priority_medium": "Medium",
            "priority_low": "Low",
            "error_date_title": "Invalid Date",
            "error_date_text": "It is not allowed to select a date earlier than today.",
            "cancel": "CANCEL",
            "delete": "DELETE",
            "confirm": "CONFIRM",
            "confirm_delete_title": "Confirm Delete",
            "confirm_delete_text": "Do you really want to delete this task?",
            "confirm_reversion_title": "Undo Completion",
            "confirm_reversion_text": "Do you want to undo the completion of this task?",
            "minhas_tarefas": "My Tasks",
            "logout": "Logout",
            "filter_priority": "Filter by Priority:",
            "all": "All",
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "register_title": "User Registration",
            "email": "Email",
            "password": "Password",
            "enter_email": "Enter your email",
            "enter_password": "Enter your password",
            "register_helper_email": "Enter your email (@ufrpe.br)",
            "register_helper_password": "Enter a password (min. 6 characters)",
            "register": "Register",
            "back_to_login": "Back to Login",
            "pending_tasks": "Pending",
            "completed_tasks": "Completed",
            "select_language": "Select Language",
            "choose_language_text": "Choose your preferred language:",
            "task_name": "Task Name",
            "task_description": "Description (optional)"
        }
    }

    @property
    def lang(self):
        return self.translations[self.language]

    def t(self, key):
        return self.translations[self.language].get(key, key)

    def build(self):
        self.theme_cls.theme_style = "Light"
        # Inicializa os textos reativos
        self.filter_all = self.t("all")
        self.filter_high = self.t("high")
        self.filter_medium = self.t("medium")
        self.filter_low = self.t("low")
        self.main_title = self.t("minhas_tarefas")
        self.filter_priority_text = self.t("filter_priority")
        self.pending_tasks_text = self.t("pending_tasks")
        self.completed_tasks_text = self.t("completed_tasks")
        return self.root

    def toggle_theme(self):
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    def on_start(self):
        self.load_tasks_from_firebase()

    def load_tasks_from_firebase(self):
        try:
            tasks_snapshot = self.db.child("tasks").get()
            if tasks_snapshot.each():
                for task in tasks_snapshot.each():
                    task_data = task.val()
                    task_data['id'] = task.key()
                    self.tasks.append(task_data)
            self.update_tasks()
        except Exception as e:
            print(f"Erro ao carregar tarefas do Firebase: {e}")

    # Métodos de Login e Cadastro
    def do_login(self, username, password):
        try:
            user = self.auth.sign_in_with_email_and_password(username, password)
            self.root.current = "main"
        except Exception as e:
            error_dialog = MDDialog(
                title=self.t("error_login_title"),
                text=self.t("error_login_text"),
                buttons=[
                    MDFlatButton(
                        text=self.t("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def do_register(self):
        self.root.current = "register"

    def register_user(self, username, password):
        if not username.strip() or not password.strip():
            error_dialog = MDDialog(
                title=self.t("error_register_title"),
                text=self.t("error_register_text"),
                buttons=[
                    MDFlatButton(
                        text=self.t("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return
        if not username.strip().endswith("@ufrpe.br"):
            error_dialog = MDDialog(
                title=self.t("domain_invalid_title"),
                text=self.t("domain_invalid_text"),
                buttons=[
                    MDFlatButton(
                        text=self.t("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return
        if len(password.strip()) < 6:
            error_dialog = MDDialog(
                title=self.t("password_invalid_title"),
                text=self.t("password_invalid_text"),
                buttons=[
                    MDFlatButton(
                        text=self.t("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return
        try:
            self.auth.create_user_with_email_and_password(username, password)
            success_dialog = MDDialog(
                title=self.t("success_title"),
                text=self.t("success_text"),
                buttons=[
                    MDFlatButton(
                        text=self.t("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: success_dialog.dismiss()
                    )
                ],
            )
            success_dialog.bind(on_dismiss=lambda *args: self.go_to_login())
            success_dialog.open()
        except Exception as e:
            error_dialog = MDDialog(
                title=self.t("error_register_title"),
                text=self.t("error_register_text"),
                buttons=[
                    MDFlatButton(
                        text=self.t("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def go_to_login(self):
        self.root.current = "login"

    def logout(self):
        self.root.current = "login"
        self.registered_username = None
        self.registered_password = None

    # Métodos para manipulação de tarefas
    def show_task_dialog(self, edit_task=None):
        if not self.dialog:
            self.dialog_content = DialogContent()
            self.dialog = MDDialog(
                title=self.t("new_task"),
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(
                        text=self.t("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="",  # Será atualizado logo abaixo
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=lambda x: self._save_task()
                    ),
                ],
            )
        if edit_task:
            self.task_to_edit = edit_task
            self.dialog.title = self.t("edit_task")
            self.dialog_content.ids.title_input.text = edit_task['title']
            self.dialog_content.ids.description_input.text = edit_task['description']
            self.dialog_content.selected_date = edit_task['date']
            self.dialog_content.selected_time = edit_task['time']
            self.dialog_content.ids.date_label.text = f"{self.t('date')}{edit_task['date']}"
            self.dialog_content.ids.time_label.text = f"{self.t('time')}{edit_task['time']}"
            self.dialog_content.priority = edit_task.get('priority', "medium")
            self.dialog_content.ids.priority_label.text = f"{self.t('priority')}{(self.t('priority_high') if edit_task.get('priority', 'medium')=='high' else (self.t('priority_medium') if edit_task.get('priority', 'medium')=='medium' else self.t('priority_low')))}"
            self.dialog.buttons[1].text = self.t("edit_task")
        else:
            self.task_to_edit = None
            self.dialog.title = self.t("new_task")
            self.dialog_content.ids.title_input.text = ""
            self.dialog_content.ids.description_input.text = ""
            self.dialog_content.selected_date = datetime.now().strftime('%d/%m/%Y')
            self.dialog_content.selected_time = datetime.now().strftime('%H:%M')
            self.dialog_content.ids.date_label.text = f"{self.t('date')}{self.dialog_content.selected_date}"
            self.dialog_content.ids.time_label.text = f"{self.t('time')}{self.dialog_content.selected_time}"
            self.dialog_content.priority = "medium"
            self.dialog_content.ids.priority_label.text = f"{self.t('priority')}{self.t('priority_medium')}"
            self.dialog.buttons[1].text = self.t("save")
        self.dialog.open()

    def _save_task(self):
        title = self.dialog_content.ids.title_input.text
        description = self.dialog_content.ids.description_input.text or ""
        date_str = self.dialog_content.selected_date
        time_str = self.dialog_content.selected_time
        priority = self.dialog_content.priority
        selected_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        if selected_date < datetime.now().date():
            error_dialog = MDDialog(
                title=self.t("error_date_title"),
                text=self.t("error_date_text"),
                buttons=[
                    MDFlatButton(
                        text=self.t("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()
            return
        if title.strip():
            # Se for edição, preserva o valor "completed" original; caso contrário, nova tarefa inicia não concluída.
            if self.task_to_edit:
                task_data = {
                    'title': title,
                    'description': description,
                    'date': date_str,
                    'time': time_str,
                    'completed': self.task_to_edit.get('completed', False),
                    'priority': priority
                }
            else:
                task_data = {
                    'title': title,
                    'description': description,
                    'date': date_str,
                    'time': time_str,
                    'completed': False,
                    'priority': priority
                }
            if self.task_to_edit:
                task_id = self.task_to_edit.get('id')
                if task_id:
                    self.db.child("tasks").child(task_id).set(task_data)
                    try:
                        idx = self.tasks.index(self.task_to_edit)
                        task_data['id'] = task_id
                        self.tasks[idx] = task_data
                    except ValueError:
                        pass
            else:
                new_task_ref = self.db.child("tasks").push(task_data)
                task_data['id'] = new_task_ref["name"]
                self.tasks.append(task_data)
            self.update_tasks()
            self.dialog.dismiss()

    def on_complete(self, checkbox, value, task_item):
        try:
            idx = self.tasks.index(task_item)
            self.tasks[idx]['completed'] = value
            task_id = task_item.get('id')
            if task_id:
                self.db.child("tasks").child(task_id).update({'completed': value})
        except ValueError:
            pass
        self.update_tasks()

    def delete_task(self, instance, task_item):
        self.task_to_delete = task_item
        self.delete_dialog = MDDialog(
            title=self.t("confirm_delete_title"),
            text=self.t("confirm_delete_text"),
            buttons=[
                MDFlatButton(
                    text=self.t("cancel"),
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.delete_dialog.dismiss()
                ),
                MDFlatButton(
                    text=self.t("delete"),
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self._confirm_delete()
                ),
            ]
        )
        self.delete_dialog.open()

    def _confirm_delete(self):
        try:
            task_id = self.task_to_delete.get('id')
            if task_id:
                self.db.child("tasks").child(task_id).remove()
            self.tasks.remove(self.task_to_delete)
        except ValueError:
            pass
        self.update_tasks()
        self.delete_dialog.dismiss()

    def revert_task(self, instance, task_item):
        self.task_to_revert = task_item
        self.revert_dialog = MDDialog(
            title=self.t("confirm_reversion_title"),
            text=self.t("confirm_reversion_text"),
            buttons=[
                MDFlatButton(
                    text=self.t("cancel"),
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.revert_dialog.dismiss()
                ),
                MDFlatButton(
                    text=self.t("confirm"),
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
            task_id = self.task_to_revert.get('id')
            if task_id:
                self.db.child("tasks").child(task_id).update({'completed': False})
        except ValueError:
            pass
        self.update_tasks()
        self.revert_dialog.dismiss()

    def update_tasks(self):
        pending_container = self.root.get_screen("main").ids.pending_tasks_container
        completed_container = self.root.get_screen("main").ids.completed_tasks_container
        pending_container.clear_widgets()
        completed_container.clear_widgets()
        filtered_tasks = [
            task for task in self.tasks
            if self.priority_filter == "all" or task.get("priority") == self.priority_filter
        ]
        def sort_key(task):
            dt_str = f"{task['date']} {task['time']}"
            return datetime.strptime(dt_str, '%d/%m/%Y %H:%M')
        pending_tasks = sorted(
            [task for task in filtered_tasks if not task['completed']],
            key=sort_key
        )
        completed_tasks = sorted(
            [task for task in filtered_tasks if task['completed']],
            key=sort_key
        )
        for task in pending_tasks:
            card = ToDoCard(
                title=task['title'],
                description=task['description'],
                date=task['date'],
                time=task['time'],
                completed=task['completed'],
                priority=task['priority']
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
                completed=task['completed'],
                priority=task['priority']
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

    def set_priority_filter(self, priority):
        self.priority_filter = priority
        self.update_tasks()

    # Métodos para seleção de idioma
    def show_language_dialog(self):
        self.language_dialog = MDDialog(
            title=self.t("select_language"),
            text=self.t("choose_language_text"),
            buttons=[
                MDFlatButton(
                    text="Português",
                    on_release=lambda x: self.set_language("pt")
                ),
                MDFlatButton(
                    text="English",
                    on_release=lambda x: self.set_language("en")
                )
            ]
        )
        self.language_dialog.open()

    def set_language(self, lang):
        self.language = lang
        # Atualiza os textos dos filtros reativos
        self.filter_all = self.t("all")
        self.filter_high = self.t("high")
        self.filter_medium = self.t("medium")
        self.filter_low = self.t("low")
        # Atualiza os textos principais
        self.main_title = self.t("minhas_tarefas")
        self.filter_priority_text = self.t("filter_priority")
        self.pending_tasks_text = self.t("pending_tasks")
        self.completed_tasks_text = self.t("completed_tasks")
        if hasattr(self, 'dialog_content'):
            self.dialog_content.update_menu_items()
            self.dialog_content.update_fields_text()
            self.dialog_content.ids.date_label.text = f"{self.t('date')}{self.dialog_content.selected_date}"
            self.dialog_content.ids.time_label.text = f"{self.t('time')}{self.dialog_content.selected_time}"
            self.dialog_content.ids.priority_label.text = f"{self.t('priority')}{(self.t('priority_high') if self.dialog_content.priority=='high' else (self.t('priority_medium') if self.dialog_content.priority=='medium' else self.t('priority_low')))}"
            self.dialog_content.ids.change_date_button.text = self.t("change_date")
            self.dialog_content.ids.change_time_button.text = self.t("change_time")
            self.dialog_content.ids.priority_dropdown.text = self.t("select_priority")
        if self.dialog:
            if self.task_to_edit is None:
                self.dialog.buttons[1].text = self.t("save")
            else:
                self.dialog.buttons[1].text = self.t("edit_task")
        self.language_dialog.dismiss()
        self.update_tasks()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []
        self.dialog = None
        self.delete_dialog = None
        self.task_to_edit = None
        self.revert_dialog = None
        self.registered_username = None
        self.registered_password = None
        self.priority_filter = "all"
        config = {
            "apiKey": "APIKEY",
            "authDomain": "Domain",
            "databaseURL": "DatabaseURL",
            "storageBucket": "storageBucket",
            "messagingSenderId": "messagingSenderId",
            "appId": "appId",
            "projectId": "projectId",
        }
        self.fb = pyrebase.initialize_app(config)
        self.db = self.fb.database()
        self.auth = self.fb.auth()
        self.bind(language=lambda instance, value: self.update_tasks())

if __name__ == '__main__':
    ToDoApp().run()
