import os
import requests
import json
import base64
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Inicializa colorama para formatação de terminal
init()

# Carrega variáveis de ambiente
load_dotenv()

class ClaudeChatbot:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key não encontrada. Adicione a ANTHROPIC_API_KEY no .env")
        
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Histórico de mensagens para manter o contexto
        self.messages = []
        
        # Carrega a base de conhecimentos da empresa
        self.company_knowledge = self.load_company_knowledge()
        
        # Contexto do sistema para o assistente
        self.system_prompt = f"""
        Você é o Kit, uma assistente de IA especializada em DevOps e onboarding de desenvolvedores.
        Seu tom é amigável, você usa emojis de chocolate 🍫 e faz piadas com chocolate ocasionalmente para manter o tema da empresa Choco-dev.
        
        Você ajuda desenvolvedores que acabaram de entrar na empresa Choco-dev a:
        - Resolver problemas de configuração de ambiente Windows e Linux para desenvolvimento de software.
        - Explicar ferramentas de devops como Docker, Kubernetes, Jenkins, GitLab CI/CD e Terraform.
        - Sugerir endereços da documentação interna e externa relevantes.
        - Oferecer tutoriais passo a passo para configuração de ambientes.
        - Explicar funcionamento de esteiras de automação da empresa.
        
        INFORMAÇÕES IMPORTANTES SOBRE A EMPRESA CHOCO-DEV:
        {self.company_knowledge}        
        Quando não souber uma resposta específica sobre processos internos da Choco-dev, 
        você deve indicar isso e sugerir que o desenvolvedor consulte a wiki interna ou 
        alguém do seu time.
        """
        
        self.welcome_message = """
        Olá! Eu sou Kit, serei a sua assistente de Onboarding na empresa Choco-dev! 🍫
        
        Como posso ajudar você hoje? 
        
        Dicas:
        🍫 Explicar alguma das ferramentas que utilizamos na empresa;
        🍫 Oferecer tutoriais para configurar o seu ambiente de desenvolvimento;
        🍫 Explicar funcionamento como fazer o deploy utilizando esteiras de automação;
        🍫 Sugerir documentação da empresa;
        🍫 Perguntar sobre fluxos de trabalho específicos da Choco-dev;
        
        Digite 'comandos' para ver opções especiais disponíveis.
        """

    def load_company_knowledge(self):
        """Carrega informações da empresa a partir de um arquivo."""
        try:
            with open("company_knowledge.txt", "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            # Conhecimento base caso o arquivo não exista
            return """
            Stack de Tecnologia: Python, React native, Node.js, PostgreSQL
            Ferramentas DevOps: Docker, Kubernetes, Jenkins, GitLab CI/CD
            Principais Projetos: ChocoPOV (sistema de ponto de venda) e ChocoAPI (API para parceiros)
            Ambientes: Desenvolvimento, Homologação, Produção
            Wiki interna: https://wiki.choco-dev.internal
            Repositório de código: GitLab em https://gitlab.choco-dev.internal
            """

    def add_document_context(self, document_path, document_name):
        """Adiciona um documento como contexto para a conversa."""
        try:
            with open(document_path, "r", encoding="utf-8") as file:
                content = file.read()
                
            # Adiciona o documento como uma mensagem do sistema
            system_message = {
                "role": "user", 
                "content": f"Aqui está um documento importante da Choco-dev que você deve usar como referência: {document_name}\n\n{content}"
            }
            self.messages.append(system_message)
            
            # Adiciona resposta a adição para manter o fluxo de conversa
            self.messages.append({
                "role": "assistant",
                "content": f"Obrigado por compartilhar o documento '{document_name}'. Vou usar essas informações para ajudar melhor nas suas dúvidas sobre a Choco-dev."
            })
            
            return True
        except Exception as e:
            print(Fore.PURPLE + f"Erro ao adicionar documento: {str(e)}" + Style.RESET_ALL)
            return False

    def send_message(self, user_input):
        # REVER ADIÇÃO DE DOC AO CONTEXTO PARA FUNCIONAR
        if user_input.lower() == "comandos":
            return self.show_commands()
        
        if user_input.lower().startswith("adicionar documento "):
            parts = user_input.split(" ", 2)
            if len(parts) == 3:
                document_path = parts[2]
                document_name = os.path.basename(document_path)
                success = self.add_document_context(document_path, document_name)
                if success:
                    return f"Documento '{document_name}' adicionado ao contexto! 🍫 Agora posso te ajudar com base nessas informações."
                else:
                    return f"Não foi possível adicionar o documento. Verifique se o caminho está correto."
        
        if user_input.lower() == "limpar contexto":
            self.messages = []
            return "Contexto da conversa foi limpo! 🍫 Mantendo apenas meu conhecimento base sobre a Choco-dev."
            
        # Append mensagem do usuário ao histórico
        self.messages.append({"role": "user", "content": user_input})
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": self.messages,
            "system": self.system_prompt,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            assistant_message = response_data["content"][0]["text"]
            
            # Append resposta do assistente ao histórico
            self.messages.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            return f"Erro ao comunicar com a API: {str(e)}"

    def show_commands(self):
        """Exibe comandos especiais disponíveis"""
        commands = """
        🍫 Comandos disponíveis:
        - 'adicionar documento [caminho]': Adiciona um documento ao contexto da conversa
        - 'limpar contexto': Remove o histórico de mensagens, mantendo apenas o conhecimento base
        - 'comandos': Mostra esta lista de comandos
        - 'sair', 'exit', 'quit': Encerra o chat
        """
        return commands

    def start_chat(self):
        print(Fore.RED + self.welcome_message + Style.RESET_ALL)
        #
        while True:
            user_input = input(Fore.WHITE + "\nVocê: " + Style.RESET_ALL)
            
            if user_input.lower() in ["sair", "exit", "quit"]:
                print(Fore.RED + "\nKit: Até logo! Foi um prazer ajudar no seu onboarding na Choco-dev! 🍫" + Style.RESET_ALL)
                break
                
            response = self.send_message(user_input)
            print(Fore.CYAN + "\nKit: " + Style.RESET_ALL + response)

    def reset_chat(self):
        self.messages = []
        print(Fore.CYAN + "Conversa reiniciada!" + Style.RESET_ALL)
        print(Fore.RED + self.welcome_message + Style.RESET_ALL)


if __name__ == "__main__":
    print(Fore.RED + "\n=== Kit & seu onboarding está sendo iniciado ===\n" + Style.RESET_ALL)
    
    try:
        chatbot = ClaudeChatbot()
        chatbot.start_chat()
    except ValueError as e:
        print(Fore.RED + f"Erro de configuração: {str(e)}" + Style.RESET_ALL)
        print("Confira a chave da API de IA no .env")
    except KeyboardInterrupt:
        print(Fore.WHITE + "\n\nEncerrando o programa. Até logo! 🍫" + Style.RESET_ALL)