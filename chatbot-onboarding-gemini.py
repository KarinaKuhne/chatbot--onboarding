import os
import requests
import json
import random
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init()
load_dotenv()

class GeminiChatbot:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key não encontrada. Adicione a GOOGLE_API_KEY no .env")
        
        # API configuration
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        self.headers = {"Content-Type": "application/json"}
        
        # Chat state tracking
        self.gemini_history = []
        self.interaction_summary = []
        self.response_count = 0
        self.max_responses = 3
        
        # Load company knowledge
        self.company_knowledge = self.load_company_knowledge()
        
        # System prompt setup
        self.system_prompt = f"""
        Você é a Kit, uma assistente de IA especializada em DevOps e onboarding de desenvolvedores.
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
        ╔════════════════════════════════════════════════════════════════════════════════════════════════════════╗
         ║    🍫 Olá, Dev Chocolateiro! 🍫                                                                     ║
        ║                                                                                                        ║
         ║    E aí? Eu sou a Kit, sua companheira de Onboarding super adocicada aqui na Choco-dev!              ║
        ║    Tô aqui pra fazer seu início na empresa ser tão suave quanto chocolate derretido!😉                 ║
         ║    O que posso colocar no seu prato hoje?                                                            ║
        ║    🍫 Te contar sobre as ferramentas deliciosas que usamos por aqui                                    ║
         ║    🍫 Dar aquela receita para configurar seu ambiente de dev rapidinho                               ║
        ║    🍫 Descomplicar o deploy nas nossas esteiras (prometo não derreter o código!)                       ║
         ║    🍫 Te mostrar onde fica a biblioteca secreta de documentação                                      ║
        ║    🍫 Bater um papo sobre como as coisas rolam aqui na fábrica de chocolates... ops, de código!        ║
         ║                                                                                                      ║
        ║    💡 Digite \"comandos\" para ver meus truques especiais ou chocolate para uma surpresa chocolatuda!  ║
         ║                                                                                                      ║        
        ╚════════════════════════════════════════════════════════════════════════════════════════════════════════╝
        """

    def load_company_knowledge(self):
        """Carrega informações da empresa a partir de um arquivo."""
        try:
            with open("./KB-CHOCODEV.txt", "r", encoding="utf-8") as file:
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
                
            # Adiciona o documento ao histórico Gemini
            self.gemini_history.append({
                "role": "user",
                "parts": [{"text": f"Aqui está um documento importante da Choco-dev que você deve usar como referência: {document_name}\n\n{content}"}]
            })
            
            # Simula uma resposta do assistente
            response_text = f"Obrigado por compartilhar o documento '{document_name}'. Vou usar essas informações para ajudar melhor nas suas dúvidas sobre a Choco-dev."
            
            # Adiciona a resposta ao histórico Gemini
            self.gemini_history.append({
                "role": "model",
                "parts": [{"text": response_text}]
            })
            
            # Registra esta interação no resumo
            self.interaction_summary.append({
                "user": f"Compartilhou documento: {document_name}",
                "assistant": response_text
            })
            
            return True
        except Exception as e:
            print(Fore.PURPLE + f"Erro ao adicionar documento: {str(e)}" + Style.RESET_ALL)
            return False
    
    def get_chocolate_fact(self):
        chocolate_facts = [
            "O chocolate contém mais de 600 compostos aromáticos diferentes! 🍫",
            "O primeiro chocolate em barra foi criado em 1847 pela Fry & Sons na Inglaterra. 🍫",
            "O chocolate branco não é tecnicamente chocolate, pois não contém cacau sólido! 🍫",
            "Uma semente de cacau contém aproximadamente 50% de gordura natural. 🍫",
            "Os suíços são os maiores consumidores de chocolate do mundo, com média de 9kg por pessoa anualmente! 🍫",
            "O chocolate contém teobromina, um composto tóxico para cães e gatos. 🍫",
            "O chocolate ao leite foi inventado na Suíça por Daniel Peter em 1876. 🍫",
            "Demora aproximadamente 400 sementes de cacau para fazer uma barra de chocolate. 🍫",
            "O chocolate derrete aproximadamente na temperatura do corpo humano (37°C). 🍫",
            "A palavra 'chocolate' vem da palavra asteca 'xocolatl'. 🍫",
            "O chocolate foi usado como moeda pelos astecas e maias. 🍫",
            "O chocolate escuro contém antioxidantes que podem ajudar a reduzir a pressão arterial. 🍫",
            "Existe um quarto tipo de chocolate além do amargo, ao leite e branco: o chocolate rubi! 🍫",
            "Um cacaueiro produz cerca de 2.500 sementes por ano - o suficiente para 2,5kg de chocolate. 🍫",
            "O chocolate era originalmente consumido como bebida, não como barra sólida. 🍫"
        ]
        
        return random.choice(chocolate_facts)
    
    def generate_interaction_summary(self):
        """Gera um resumo dinâmico dos 3 assuntos principais usando análise das interações."""
        if len(self.interaction_summary) == 0:
            return "Não houve interações nesta sessão para resumir."
        
        summary = """
        ╔══════════════════════════════════════════════════════════╗
        ║    🍫 RESUMO DA NOSSA CONVERSA CHOCOLATUDA 🍫           ║
        ╚══════════════════════════════════════════════════════════╝
        
        """
        
        # Categorizar as interações para identificar os principais tópicos
        topics = {
            "empresa": [],
            "devops": [],
            "ambiente": [], 
            "esteiras": [],
            "tecnologias": [],
            "documentação": [],
            "humor": []
        }
        
        # Coletar mensagens por categoria
        for interaction in self.interaction_summary:
            user_message = interaction['user'].lower()
            assistant_response = interaction['assistant']
            
            # Armazenar o par completo de mensagens para cada categoria relevante
            if any(term in user_message for term in ["empresa", "choco-dev", "choco dev", "sobre a empresa"]):
                topics["empresa"].append((user_message, assistant_response))
                
            if any(term in user_message for term in ["docker", "kubernetes", "devops", "jenkins", "gitlab"]):
                topics["devops"].append((user_message, assistant_response))
                
            if any(term in user_message for term in ["ambiente", "configuração", "setup", "instalar"]):
                topics["ambiente"].append((user_message, assistant_response))
                
            if any(term in user_message for term in ["esteira", "cicd", "ci/cd", "pipeline", "deploy"]):
                topics["esteiras"].append((user_message, assistant_response))
                
            if any(term in user_message for term in ["python", "javascript", "node", "react", "stack", "tecnologia"]):
                topics["tecnologias"].append((user_message, assistant_response))
                
            if any(term in user_message for term in ["documento", "documentação", "wiki", "manual"]):
                topics["documentação"].append((user_message, assistant_response))
                
            if any(term in user_message for term in ["piada", "chocolate", "brincadeira", "curiosidade"]):
                topics["humor"].append((user_message, assistant_response))
        
        # Ordenar tópicos por frequência de menções
        top_topics = sorted([(topic, len(messages)) for topic, messages in topics.items()], 
                        key=lambda x: x[1], reverse=True)[:3]
        
        # Nomes amigáveis para os tópicos
        topic_names = {
            "empresa": "sobre a empresa Choco-dev",
            "devops": "sobre ferramentas de DevOps",
            "ambiente": "sobre configuração de ambiente",
            "esteiras": "sobre processos de CI/CD",
            "tecnologias": "sobre o stack tecnológico",
            "documentação": "sobre recursos de documentação",
            "humor": "sobre curiosidades de chocolate"
        }
        
        # Gerar resumos para os 3 tópicos principais usando o conteúdo das interações
        summary += "Aqui está um resumo dos principais pontos que discutimos:\n\n"
        
        for i, (topic, count) in enumerate(top_topics, 1):
            if count > 0:  # Só incluir tópicos que realmente foram discutidos
                # Extrair palavras-chave e frases importantes das interações sobre este tópico
                key_phrases = []
                for user_msg, assistant_msg in topics[topic]:
                    # Extrair frases importantes da resposta do assistente
                    sentences = [s.strip() for s in assistant_msg.split('.') if len(s.strip()) > 20]
                    # Selecionar até 2 frases mais informativas (mais longas)
                    key_sentences = sorted(sentences, key=len, reverse=True)[:2]
                    key_phrases.extend(key_sentences)
                
                # Criar um parágrafo resumido com base nas frases extraídas
                if key_phrases:
                    # Selecionar informações mais relevantes
                    content = ". ".join(key_phrases[:3])
                    
                    # Adicionar introdução contextual com base no tópico
                    intro_phrases = {
                        "empresa": "Conversamos sobre a estrutura e cultura da Choco-dev",
                        "devops": "Exploramos as ferramentas DevOps utilizadas pela empresa",
                        "ambiente": "Discutimos a configuração do ambiente de desenvolvimento",
                        "esteiras": "Abordamos os processos de CI/CD da Choco-dev",
                        "tecnologias": "Analisamos o stack tecnológico dos projetos",
                        "documentação": "Vimos os recursos de documentação disponíveis",
                        "humor": "Compartilhamos momentos descontraídos com curiosidades"
                    }
                    
                    # Construir parágrafo combinando introdução e conteúdo extraído
                    paragraph = f"{intro_phrases[topic]}. {content}"
                    
                    # Garantir que termine com ponto final e adicionar emoji chocolate
                    if not paragraph.endswith('.'):
                        paragraph += '.'
                    paragraph += ' 🍫'
                    
                    summary += f"🍫 **{topic_names[topic].capitalize()}**\n"
                    summary += f"{paragraph}\n\n"
                else:
                    # Fallback se não houver conteúdo suficiente
                    summary += f"🍫 **{topic_names[topic].capitalize()}**\n"
                    summary += f"Conversamos sobre {topic_names[topic]}, abordando pontos importantes para seu onboarding na Choco-dev. 🍫\n\n"
        
        summary += """
        ╔══════════════════════════════════════════════════════════╗
        ║    Obrigado por usar a Kit, seja bem vindo a empresa! 🍫 ║
        ║    O chat será encerrado agora.                          ║
        ╚══════════════════════════════════════════════════════════╝
        """
        
        return summary

    def send_message(self, user_input):
        # Verifica se o limite de respostas foi atingido
        if self.response_count >= self.max_responses:
            summary = self.generate_interaction_summary()
            self.reset_chat()
            return summary, True  # Retorna o resumo e sinaliza para sair
        
        # Comandos especiais
        if user_input.lower() == "comandos":
            return self.show_commands(), False
        
        if user_input.lower() == "reiniciar":
            if self.response_count > 0:
                summary = self.generate_interaction_summary()
                self.reset_chat()
                return summary + "\n\nChat reiniciado! Agora você tem 3 novas interações disponíveis. 🍫", False
            else:
                self.reset_chat()
                return "Chat reiniciado! Agora você tem 3 novas interações disponíveis. 🍫", False
        
        if user_input.lower().startswith("adicionar documento "):
            parts = user_input.split(" ", 2)
            if len(parts) == 3:
                document_path = parts[2]
                document_name = os.path.basename(document_path)
                success = self.add_document_context(document_path, document_name)
                if success:
                    return f"Documento '{document_name}' adicionado ao contexto! 🍫 Agora posso te ajudar com base nessas informações.", False
                else:
                    return f"Não foi possível adicionar o documento. Verifique se o caminho está correto.", False
        
        if user_input.lower() == "limpar contexto":
            self.gemini_history = []
            self.interaction_summary = []
            return "Contexto da conversa foi limpo! 🍫 Mantendo apenas meu conhecimento base sobre a Choco-dev.", False

        # Easter egg do chocolate
        if user_input.strip() == "chocolate":
            fact = self.get_chocolate_fact()
            
            # Registra esta interação no resumo
            self.interaction_summary.append({
                "user": "Solicitou um fato sobre chocolate",
                "assistant": fact
            })
            
            self.response_count += 1
            
            # Adiciona informação sobre interações restantes
            remaining = self.max_responses - self.response_count
            if remaining > 0:
                fact += f"\n\n[Você ainda tem {remaining} interação(ões) disponível(is) nesta sessão]"
                
            return fact, self.response_count >= self.max_responses

        # Adiciona a mensagem ao formato Gemini
        self.gemini_history.append({
            "role": "user",
            "parts": [{"text": user_input}]
        })
        
        # Prepara a requisição para o Gemini
        request_data = {
            "contents": self.gemini_history,
            "generationConfig": {
                "temperature": 0.88,
                "maxOutputTokens": 1000,
                "topP": 0.95
            }
        }
        
        # Adiciona o system prompt como instrução do sistema
        if self.system_prompt:
            request_data["systemInstruction"] = {
                "parts": [{"text": self.system_prompt}]
            }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=request_data
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Extrai a resposta do formato da API do Gemini
            assistant_message = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Adiciona ao histórico Gemini 
            self.gemini_history.append({
                "role": "model",
                "parts": [{"text": assistant_message}]
            })
            
            # Registra esta interação no resumo (limitando o tamanho para não ficar muito grande)
            user_message_short = user_input[:200] + "..." if len(user_input) > 200 else user_input
            
            self.interaction_summary.append({
                "user": user_message_short,
                "assistant": assistant_message
            })
            
            # Incrementa o contador de respostas
            self.response_count += 1
            
            # Adiciona informação sobre interações restantes
            remaining = self.max_responses - self.response_count
            if remaining > 0:
                assistant_message += f"\n\n[Você ainda tem {remaining} interação(ões) disponível(is) nesta sessão]"
            
            # Verifica se atingiu o limite máximo
            should_exit = self.response_count >= self.max_responses
            
            return assistant_message, should_exit
            
        except requests.exceptions.RequestException as e:
            error_message = f"Erro ao comunicar com a API: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_message += f"\nDetalhes: {json.dumps(error_detail, indent=2)}"
                except:
                    error_message += f"\nCódigo de status: {e.response.status_code}"
            return error_message, False

    def show_commands(self):
        """Exibe comandos especiais disponíveis"""
        commands = """
        🍫 Comandos disponíveis:
        - 'adicionar documento [caminho]': Adiciona um documento ao contexto da conversa
        - 'limpar contexto': Remove o histórico de mensagens, mantendo apenas o conhecimento base
        - 'reiniciar': Reinicia o chat e reseta o contador de interações (gera resumo se houver interações)
        - 'comandos': Mostra esta lista de comandos
        - 'chocolate': Easter egg
        - 'sair', 'exit', 'quit': Encerra o chat
        """
        return commands

    def start_chat(self):
        print(Fore.RED + self.welcome_message + Style.RESET_ALL)
        
        while True:
            user_input = input(Fore.WHITE + "\nVocê: " + Style.RESET_ALL)
            
            if user_input.lower() in ["sair", "exit", "quit"]:
                if self.response_count > 0:
                    summary = self.generate_interaction_summary()
                    print(Fore.CYAN + "\nKit: " + Style.RESET_ALL + summary)
                else:
                    print(Fore.RED + "\nKit: Até logo! Foi um prazer ajudar no seu onboarding na Choco-dev! 🍫" + Style.RESET_ALL)
                break
                
            response, should_exit = self.send_message(user_input)
            print(Fore.RED + "\nKit: " + Style.RESET_ALL + response)
            
            # Se atingiu o limite de interações, exibe o resumo e sai automaticamente
            if should_exit:
                summary = self.generate_interaction_summary()
                print(Fore.RED + "\nKit: " + Style.RESET_ALL + summary)
                break

    def reset_chat(self):
        self.gemini_history = []
        self.interaction_summary = []
        self.response_count = 0
        print(Fore.RED + "Conversa reiniciada!" + Style.RESET_ALL)
        print(Fore.RED + self.welcome_message + Style.RESET_ALL)


if __name__ == "__main__":
    print(Fore.RED + "\n=== Carregando o sistema ===\n" + Style.RESET_ALL)
    
    try:
        chatbot = GeminiChatbot()
        chatbot.start_chat()
        print(Fore.WHITE + "\n\nEncerrando o programa. Até logo! 🍫" + Style.RESET_ALL)
    except ValueError as e:
        print(Fore.RED + f"Erro de configuração: {str(e)}" + Style.RESET_ALL)
        print("Confira a chave da API de IA no .env como GOOGLE_API_KEY=sua_chave_aqui")
    except KeyboardInterrupt:
        print(Fore.WHITE + "\n\nEncerrando o programa. Até logo! 🍫" + Style.RESET_ALL)