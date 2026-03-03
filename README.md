# 🤖 Bot de Auditoria e Emissão de CND - Betha Sistemas

Esta é uma solução robusta de automação desenvolvida em Python para otimizar o processo de extração, emissão e análise de Certidões Negativas de Débitos (CND) no Portal do Cidadão da Betha Sistemas. O projeto foca na redução do tempo de auditoria manual e na eliminação de falhas humanas na organização de arquivos.

## 🌟 Principais Funcionalidades

* **Segurança e Ética**: Implementação de variáveis de ambiente (`.env`) para proteger URLs governamentais e caminhos de diretórios locais, mantendo o código genérico e seguro para portfólio.
* **Análise Heurística de PDF**: Integração com a biblioteca `PyPDF2` para leitura automatizada do conteúdo das certidões, permitindo a classificação imediata entre **NEGATIVA** ou **POSITIVA**.
* **Extração com Regex**: Utilização de Expressões Regulares para isolar o nome dos produtores, removendo automaticamente endereços rurais e dados irrelevantes para a nomenclatura dos arquivos.
* **Bypass de Interface**: Uso estratégico de `PyAutoGUI` para interagir com modais do sistema operacional e garantir o salvamento correto dos documentos.
* **Gestão de Downloads**: Lógica de monitoramento de diretório com tratamento de exceções para evitar conflitos de escrita e leitura de arquivos pelo Windows.

## 🧠 Integração com IA Generativa
Este projeto utilizou IA Generativa (Gemini) como copiloto estratégico para:
* **Otimização de Lógica**: Refinamento de algoritmos de busca e tratamento de exceções para aumentar a resiliência do bot.
* **Engenharia de Regex**: Desenvolvimento de expressões regulares complexas para extração precisa de nomes e dados em documentos PDF variados.
* **Qualidade de Código**: Revisão de boas práticas e estruturação de funções para garantir um código limpo e de fácil manutenção.

## 🛠️ Tecnologias Utilizadas

* **Python 3.12+**
* **Selenium**: Automação de navegação web.
* **PyAutoGUI**: Automação de interface gráfica (teclado/mouse).
* **PyPDF2 & pdfplumber**: Processamento e extração de dados de arquivos PDF.
* **Python-Dotenv**: Gestão de configurações e variáveis de ambiente.

## ⚙️ Configuração

1. Instale as dependências necessárias:
   ```bash
   pip install selenium pyautogui webdriver-manager PyPDF2 python-dotenv pdfplumber
2. Configure seu arquivo .env na raiz do projeto:
   ```bash
   ARQUIVO_FONTE=relatorio_sicas.pdf
   SITE_PREFEITURA=[https://link-da-prefeitura.gov.br](https://link-da-prefeitura.gov.br)
   DOWNLOAD_CERTIDAO=D:\Caminho\Para\Sua\Pasta
   URL_BETHA_SISTEMA=[https://link-do-sistema.faces](https://link-do-sistema.faces)

## 📋 Como usar
1. Coloque o PDF gerado pelo Sistema na pasta do projeto.
2. Execute o script principal: ````python bot_cnd.py.````
3. O bot irá processar a lista, baixar as certidões e renomeá-las automaticamente seguindo o padrão:
````CND_STATUS_NOME_DO_PRODUTOR.pdf````
