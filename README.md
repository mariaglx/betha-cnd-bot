# Bot de Emissão de CND - Betha Sistemas (São João do Oeste/SC) 🚜

Este projeto é uma automação desenvolvida em **Python** utilizando **Selenium** e **PyAutoGUI** para emitir Certidões Negativas de Débitos (CND) de forma automatizada através do Portal do Cidadão.

## 🚀 Funcionalidades

* **Extração de Dados**: Lê uma lista de produtores/CPFs diretamente de um arquivo PDF (Sicas).
* **Navegação Automatizada**: Realiza o login e navegação no sistema Betha até a área de emissão.
* **Bypass de Modal**: Utiliza comandos de hardware (PyAutoGUI) para interagir com o visualizador de PDF e salvar o arquivo.
* **Organização de Arquivos**: Renomeia automaticamente os PDFs baixados com o nome do produtor e CPF para facilitar a conferência.

## 🛠️ Tecnologias Utilizadas

* [Python](https://www.python.org/) - Linguagem principal.
* [Selenium](https://www.selenium.dev/) - Automação de navegador.
* [PyAutoGUI](https://pyautogui.readthedocs.io/) - Interação com interface gráfica e teclado.
* [WebDriver Manager](https://pypi.org/project/webdriver-manager/) - Gerenciamento automático do driver do Chrome.

## 📋 Pré-requisitos

Antes de rodar o bot, você precisará instalar as dependências:

```bash
pip install selenium pyautogui webdriver-manager PyPDF2
