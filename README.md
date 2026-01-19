# 📖 utilities.doc_reader

Um assistente de IA especializado em leitura e busca semântica em sites de documentação técnica. O projeto utiliza a técnica de **RAG (Retrieval-Augmented Generation)** para fornecer respostas precisas baseadas exclusivamente no conteúdo da URL fornecida.

## 🚀 Funcionalidades

- **Crawler Recursivo**: Navega automaticamente pelos links da documentação para indexar múltiplas páginas.
- **Busca Semântica**: Utiliza Embeddings locais (`all-MiniLM-L6-v2`) para entender o contexto das perguntas, indo além de simples palavras-chave.
- **Integração com Mistral AI**: Processamento de linguagem natural de última geração para formular respostas técnicas claras.
- **Arquitetura Híbrida**: Embeddings processados localmente (economia e privacidade) + LLM via API (inteligência).
- **Totalmente Dockerizado**: Ambiente isolado e fácil de subir em qualquer máquina.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.11
- **Orquestração de IA:** [LangChain](https://www.langchain.com/)
- **LLM:** [Mistral AI](https://mistral.ai/)
- **Banco de Dados Vetorial:** [ChromaDB](https://www.trychroma.com/)
- **Embeddings:** HuggingFace (Sentence Transformers)
- **Containerização:** Docker & Docker Compose

## 📋 Pré-requisitos

Antes de começar, você precisará de:
1. Uma chave de API da Mistral AI (obtenha em [console.mistral.ai](https://console.mistral.ai/)).
2. Docker e Docker Compose instalados.

## ⚙️ Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/GuDevBot/utilities.doc_reader.git
   cd utilities.doc_reader 
   ```
2. Crie um arquivo .env na raíz do projeto:
   ```bash
   AI_KEY=seu_token_da_mistral_aqui
   TARGET_URL=https://docs.python.org/3/library/
   ANONYMIZED_TELEMETRY=False
   ```

## 🏃 Como Rodar

Execute o seguinte comando no terminal:
   ```
   docker compose run --service-ports rag-crawler
   ```

O sistema irá:
   1. Mapear a URL fornecida.
   2. Baixar e processar o conteúdo.
   3. Criar o banco de dados vetorial localmente.
   4. Iniciar o chat interativo no terminal.

## 📂 Persistência de Dados

O banco de dados gerado é armazenado na pasta local ./chroma_db_data. Isso garante que:
   - Você não precise indexar o site toda vez que iniciar o programa.
   - O histórico de documentos persista mesmo após desligar o container Docker.

## Desenvolvido por Gustavo Brandi Alves