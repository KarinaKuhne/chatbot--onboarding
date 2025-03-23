# 🍫 Kit - Chatbot de Onboarding Choco-dev 🍫

Um assistente de onboarding interativo para desenvolvedores recém-chegados à empresa fictícia Choco-dev, utilizando a API do Google Gemini.

## ✨ Funcionalidades

- 🤖 Assistente virtual especializado em DevOps e onboarding
- 🛠️ Ajuda com configuração de ambientes Windows e Linux
- 📚 Acesso a informações sobre ferramentas e processos da empresa
- 🔄 Fornece tutoriais passo a passo
- 📝 Gera resumo das interações ao final da sessão
- 🍫 Tem uma personalidade amigável com tema de chocolate!

## 🛠️ Pré requisitos:

- Python 3.7+
- pip
- Chave API do Google Gemini
- 💡Dica: esta API é gratuita e pode ser gerada a partir do AI Studio do Google: https://aistudio.google.com/
- Bibliotecas (ver no requirements.txt):
  - requests
  - python-dotenv
  - colorama

## 🚀 Como Instalar

1. Clone o repositório:
```bash
git clone https://github.com/KarinaKuhne/chatbot--onboarding.git
cd chatbot--onboarding
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto com sua chave API do Google:
```
GOOGLE_API_KEY=sua_chave_aqui
```

## 💻 Como Rodar

Ative o venv:
```bash
python -m venv venv
```
Execute o script principal:
```bash
python chatbot-onboarding-gemini.py
```

### Comandos especiais:

- `adicionar documento [caminho]`: Adiciona documentação ao contexto
- `limpar contexto`: Limpa o histórico da conversa
- `reiniciar`: Reinicia o chat e o contador de interações
- `comandos`: Mostra lista de comandos disponíveis
- `chocolate`: Mostra uma curiosidade sobre chocolate
- `sair`, `exit`, `quit`: Encerra o chat

## 📊 Limitações

- Responde a apenas 3 interações por sessão
- Gera um resumo automaticamente ao final da sessão

## 🔮 Personalização

Adicione documentos de conhecimento da empresa no arquivo `KB-CHOCODEV.txt` para melhorar as respostas do chatbot.
