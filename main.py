# Importa bibliotecas necessárias para integração com Firebase, construção de interface gráfica com Kivy e KivyMD
import pyrebase  # Biblioteca para interagir com o Firebase
from kivy.uix.screenmanager import ScreenManager, Screen  # Gerencia múltiplas telas
from kivymd.app import MDApp  # Classe base para aplicativos KivyMD
from kivy.properties import StringProperty, BooleanProperty, OptionProperty  # Propriedades reativas para uso em KV
from kivymd.uix.boxlayout import MDBoxLayout  # Layout do KivyMD baseado em BoxLayout
from kivymd.uix.dialog import MDDialog  # Caixa de diálogo do KivyMD
from kivymd.uix.button import MDFlatButton, MDIconButton  # Botões do KivyMD
from kivymd.uix.pickers import MDDatePicker, MDTimePicker  # Componentes para seleção de data e hora
from datetime import datetime  # Para manipulação de datas e horários
from kivy.core.window import Window  # Permite manipulação das propriedades da janela
from kivymd.uix.menu import MDDropdownMenu  # Menu suspenso do KivyMD
# Importações para construção de abas personalizadas
from kivy.uix.boxlayout import BoxLayout  # Layout básico do Kivy
from kivymd.uix.tab import MDTabsBase  # Base para criação de abas no KivyMD

# Define o tamanho da janela da aplicação
Window.size = (350, 600)

# --------------------------
# Definição das TELAS
# --------------------------
class LoginScreen(Screen):
    # Tela de login (definida no arquivo KV)
    pass

class RegisterScreen(Screen):
    # Tela de cadastro de usuário (definida no arquivo KV)
    pass

class MainScreen(Screen):
    # Tela principal da aplicação (lista de tarefas)
    pass

# Classe customizada para as abas, combinando BoxLayout e MDTabsBase para uso em MDTabs  
class MyTab(BoxLayout, MDTabsBase):
    pass

# --------------------------
# CONTEÚDO DO DIÁLOGO PARA CADASTRAR/EDITAR TAREFAS
# --------------------------
class DialogContent(MDBoxLayout):
    # Propriedades para que o KV reconheça e atualize os valores de data e hora
    selected_date = StringProperty()
    selected_time = StringProperty()
    priority = OptionProperty("medium", options=["high", "medium", "low"])  # Prioridade: alta, média ou baixa

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inicializa com a data e horário atuais
        self.selected_date = datetime.now().strftime('%d/%m/%Y')
        self.selected_time = datetime.now().strftime('%H:%M')
        # Configuração do menu suspenso de prioridade
        self.menu_items = [
            {"text": "Alta", "viewclass": "OneLineListItem", "on_release": lambda x="high": self.set_priority(x)},
            {"text": "Média", "viewclass": "OneLineListItem", "on_release": lambda x="medium": self.set_priority(x)},
            {"text": "Baixa", "viewclass": "OneLineListItem", "on_release": lambda x="low": self.set_priority(x)},
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.priority_dropdown,
            items=self.menu_items,
            position="auto",
            width_mult=4,
        )

    def set_priority(self, priority):
        self.priority = priority
        self.menu.dismiss()
        self.ids.priority_label.text = f"Prioridade: {priority.capitalize()}"

    def show_date_picker(self):
        # Exibe o seletor de data, limitando a data mínima para a data atual (não permite datas anteriores)
        date_dialog = MDDatePicker(min_date=datetime.now().date())
        date_dialog.bind(on_save=self.on_date_save)  # Liga o evento de salvar data à função on_date_save
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        # Função chamada ao salvar a data selecionada no seletor
        # Verifica se a data selecionada é válida (não anterior à data atual)
        selected = value if hasattr(value, "year") else datetime.now().date()
        if selected < datetime.now().date():
            # Se a data for inválida, exibe um diálogo de erro
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
            return  # Não atualiza a data
        # Atualiza a propriedade com a data formatada
        self.selected_date = selected.strftime('%d/%m/%Y')
        # Atualiza o label na interface
        self.ids.date_label.text = f"Data: {self.selected_date}"

    def show_time_picker(self):
        # Exibe o seletor de horário
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.on_time_save)  # Liga o evento de salvar tempo à função on_time_save
        time_dialog.open()

    def on_time_save(self, instance, time_obj):
        # Função chamada ao salvar o horário selecionado
        # Se o objeto não possuir o método strftime, define um horário padrão
        if not hasattr(time_obj, "strftime"):
            self.selected_time = "00:00"
        else:
            self.selected_time = time_obj.strftime("%H:%M")
        # Atualiza o label na interface com o horário selecionado
        self.ids.time_label.text = f"Horário: {self.selected_time}"

# --------------------------
# CARD DE TAREFA (USADO NA LISTA DE TAREFAS)
# --------------------------
class ToDoCard(MDBoxLayout):
    # Define propriedades para título, descrição, data, horário, status de conclusão e prioridade
    title = StringProperty()
    description = StringProperty()
    date = StringProperty()
    time = StringProperty()
    completed = BooleanProperty(False)
    priority = OptionProperty("medium", options=["high", "medium", "low"])  # Prioridade: alta, média ou baixa

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Permite que o tamanho vertical do card se ajuste ao conteúdo
        self.adaptive_height = True

# --------------------------
# APLICATIVO PRINCIPAL
# --------------------------
class ToDoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Lista para armazenar as tarefas carregadas ou criadas
        self.tasks = []
        # Diálogos utilizados na aplicação (inicialmente None)
        self.dialog = None
        self.delete_dialog = None
        self.task_to_edit = None
        self.revert_dialog = None
        # Armazena as credenciais do usuário cadastrado
        self.registered_username = None
        self.registered_password = None
        # Filtro de prioridade
        self.priority_filter = "all"  # Pode ser "all", "high", "medium" ou "low"
        # --------------------------
        # CONFIGURAÇÃO DO FIREBASE
        # --------------------------
        config = {
            "apiKey": "Sua_Chave_API",
            "authDomain": "Domain",
            "databaseURL": "Database_URL",
            "storageBucket": "Storage_Bucket",
            "messagingSenderId": "MSID",
            "appId": "AppID",
            "projectId": "ProjectID"
        }
        # Inicializa a conexão com o Firebase
        self.fb = pyrebase.initialize_app(config)
        self.db = self.fb.database()  # Referência ao banco de dados
        self.auth = self.fb.auth()     # Referência à autenticação do Firebase

    def build(self):
        # Define o tema inicial como claro
        self.theme_cls.theme_style = "Light"
        # Retorna a raiz da interface, que será definida via arquivo KV
        return self.root

    def toggle_theme(self):
        # Alterna entre os modos claro e escuro
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    def on_start(self):
        # Carrega as tarefas do Firebase ao iniciar o aplicativo
        self.load_tasks_from_firebase()

    def load_tasks_from_firebase(self):
        try:
            # Obtém as tarefas armazenadas no nó "tasks" do Firebase
            tasks_snapshot = self.db.child("tasks").get()
            if tasks_snapshot.each():
                for task in tasks_snapshot.each():
                    task_data = task.val()
                    # Armazena a chave (ID) da tarefa para futuras referências
                    task_data['id'] = task.key()
                    self.tasks.append(task_data)
            # Atualiza a interface com as tarefas carregadas
            self.update_tasks()
        except Exception as e:
            print(f"Erro ao carregar tarefas do Firebase: {e}")

    # --------------------------
    # MÉTODOS DE LOGIN E CADASTRO DE USUÁRIO
    # --------------------------
    def do_login(self, username, password):
        try:
            # Tenta realizar o login com o e-mail e senha fornecidos
            user = self.auth.sign_in_with_email_and_password(username, password)
            # Se o login for bem-sucedido, muda para a tela principal
            self.root.current = "main"
        except Exception as e:
            # Em caso de erro, exibe um diálogo informando que o login falhou
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
        # Muda para a tela de cadastro de usuário
        self.root.current = "register"

    def register_user(self, username, password):
        # Valida se os campos de usuário e senha não estão vazios
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
        # Validação para permitir apenas e-mails com o domínio "@ufrpe.br"
        if not username.strip().endswith("@ufrpe.br"):
            error_dialog = MDDialog(
                title="Domínio Inválido",
                text="O e-mail deve possuir o domínio @ufrpe.br.",
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
        # Validação para que a senha tenha no mínimo 6 caracteres
        if len(password.strip()) < 6:
            error_dialog = MDDialog(
                title="Senha Inválida",
                text="A senha deve conter pelo menos 6 caracteres.",
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
        try:
            # Cria um novo usuário no Firebase com os dados fornecidos
            self.auth.create_user_with_email_and_password(username, password)
            # Exibe um diálogo de sucesso e, ao ser fechado, redireciona para a tela de login
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
            success_dialog.bind(on_dismiss=lambda *args: self.go_to_login())
            success_dialog.open()
        except Exception as e:
            # Em caso de erro no cadastro, exibe um diálogo informando a falha
            error_dialog = MDDialog(
                title="Erro no Cadastro",
                text="Não foi possível cadastrar o usuário.",
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

    def go_to_login(self):
        # Muda para a tela de login
        self.root.current = "login"

    # --------------------------
    # MÉTODO PARA LOGOUT
    # --------------------------
    def logout(self):
        # Limpa as credenciais do usuário e retorna à tela de login
        self.root.current = "login"
        self.registered_username = None
        self.registered_password = None

    # --------------------------
    # MÉTODOS PARA MANIPULAÇÃO DAS TAREFAS
    # --------------------------
    def show_task_dialog(self, edit_task=None):
        """
        Exibe o diálogo para criar ou editar uma tarefa.
        Se 'edit_task' for fornecida, os campos serão pré-preenchidos com os dados da tarefa.
        """
        if not self.dialog:
            # Cria o conteúdo do diálogo utilizando a classe DialogContent
            self.dialog_content = DialogContent()
            self.dialog = MDDialog(
                title="Nova Tarefa",
                type="custom",  # Define que o conteúdo do diálogo é customizado
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
            # Caso seja uma edição, preenche os campos com os dados da tarefa existente
            self.task_to_edit = edit_task
            self.dialog.title = "Editar Tarefa"
            self.dialog_content.ids.title_input.text = edit_task['title']
            self.dialog_content.ids.description_input.text = edit_task['description']
            self.dialog_content.selected_date = edit_task['date']
            self.dialog_content.selected_time = edit_task['time']
            self.dialog_content.ids.date_label.text = f"Data: {edit_task['date']}"
            self.dialog_content.ids.time_label.text = f"Horário: {edit_task['time']}"
            self.dialog_content.priority = edit_task.get('priority', "medium")  # Define a prioridade
            self.dialog_content.ids.priority_label.text = f"Prioridade: {edit_task.get('priority', 'medium').capitalize()}"
        else:
            # Se for uma nova tarefa, limpa os campos e define os valores padrão (data e horário atuais)
            self.task_to_edit = None
            self.dialog.title = "Nova Tarefa"
            self.dialog_content.ids.title_input.text = ""
            self.dialog_content.ids.description_input.text = ""
            self.dialog_content.selected_date = datetime.now().strftime('%d/%m/%Y')
            self.dialog_content.selected_time = datetime.now().strftime('%H:%M')
            self.dialog_content.ids.date_label.text = f"Data: {self.dialog_content.selected_date}"
            self.dialog_content.ids.time_label.text = f"Horário: {self.dialog_content.selected_time}"
            self.dialog_content.priority = "medium"  # Prioridade padrão
            self.dialog_content.ids.priority_label.text = "Prioridade: Média"  # Prioridade padrão
        self.dialog.open()

    def _save_task(self):
        # Recupera os dados inseridos no diálogo
        title = self.dialog_content.ids.title_input.text
        description = self.dialog_content.ids.description_input.text or ""
        date_str = self.dialog_content.selected_date
        time_str = self.dialog_content.selected_time
        priority = self.dialog_content.priority
        # Validação: impede salvar tarefa com data anterior à data atual
        selected_date = datetime.strptime(date_str, '%d/%m/%Y').date()
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
            return  # Interrompe o salvamento
            
        if title.strip():
            # Monta o dicionário com os dados da tarefa
            task_data = {
                'title': title,
                'description': description,
                'date': date_str,
                'time': time_str,
                'completed': False,
                'priority': priority
            }
            if self.task_to_edit:
                # Se for edição, atualiza a tarefa no Firebase usando o ID armazenado
                task_id = self.task_to_edit.get('id')
                if task_id:
                    self.db.child("tasks").child(task_id).set(task_data)
            else:
                # Se for nova tarefa, adiciona ao Firebase e armazena a chave gerada
                new_task_ref = self.db.child("tasks").push(task_data)
                task_data['id'] = new_task_ref["name"]
                self.tasks.append(task_data)
            # Atualiza a lista de tarefas na interface e fecha o diálogo
            self.update_tasks()
            self.dialog.dismiss()

    def on_complete(self, checkbox, value, task_item):
        # Atualiza o status de conclusão da tarefa (tanto localmente quanto no Firebase)
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
        # Exibe uma caixa de diálogo para confirmar a exclusão da tarefa
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
        # Remove a tarefa do Firebase e da lista local, após confirmação
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
        # Exibe uma caixa de diálogo para confirmar a reversão da conclusão da tarefa
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
        # Altera o status da tarefa para não concluída e atualiza no Firebase
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
        # Atualiza a lista de tarefas na interface, separando as pendentes das concluídas
        pending_container = self.root.get_screen("main").ids.pending_tasks_container
        completed_container = self.root.get_screen("main").ids.completed_tasks_container
        # Limpa os containers antes de re-adicionar as tarefas
        pending_container.clear_widgets()
        completed_container.clear_widgets()
        # Filtra as tarefas com base na prioridade selecionada
        filtered_tasks = [
            task for task in self.tasks
            if self.priority_filter == "all" or task.get("priority") == self.priority_filter
        ]
        # Função de ordenação baseada na data e hora da tarefa
        def sort_key(task):
            dt_str = f"{task['date']} {task['time']}"
            return datetime.strptime(dt_str, '%d/%m/%Y %H:%M')
        # Separa e ordena as tarefas pendentes e concluídas
        pending_tasks = sorted(
            [task for task in filtered_tasks if not task['completed']],
            key=sort_key
        )
        completed_tasks = sorted(
            [task for task in filtered_tasks if task['completed']],
            key=sort_key
        )
        # Cria os cards para as tarefas pendentes e os adiciona no container correspondente
        for task in pending_tasks:
            card = ToDoCard(
                title=task['title'],
                description=task['description'],
                date=task['date'],
                time=task['time'],
                completed=task['completed'],
                priority=task['priority']
            )
            # Liga os eventos de clique dos botões às funções correspondentes
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
        # Cria os cards para as tarefas concluídas e os adiciona no container correspondente
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
        # Define o filtro de prioridade e atualiza a lista de tarefas
        self.priority_filter = priority
        self.update_tasks()

# Execução da aplicação apenas se o arquivo for executado diretamente
if __name__ == '__main__':
    ToDoApp().run()