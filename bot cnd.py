import pdfplumber
import re
import time
import os
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 

# --- PARTE 1: EXTRAÇÃO ---
def extrair_dados_sicas(caminho_pdf):
    print("🔍 Lendo Relatório Sicas...")
    dados = []
    padrao_cpf = r'(\d{3}\.?\d{3}\.?\d{3}-?\d{2})'
    
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                linhas = texto.split('\n')
                for linha in linhas:
                    cpf_enc = re.search(padrao_cpf, linha)
                    if cpf_enc:
                        cpf_limpo = cpf_enc.group(1).replace('.','').replace('-','')
                        nome_bruto = linha.split(cpf_enc.group(1))[0].strip()
                        nome_limpo = re.sub(r'[^a-zA-Z ]', '', nome_bruto).strip()
                        dados.append({'cpf': cpf_limpo, 'nome': nome_limpo or "Produtor"})
    
    vistos = set()
    lista_final = []
    for d in dados:
        if d['cpf'] not in vistos:
            lista_final.append(d)
            vistos.add(d['cpf'])
            
    print(f"✅ {len(lista_final)} produtores encontrados.")
    return lista_final

# --- PARTE 2: ROBÔ ---
def executar_robo_cnd(lista_produtores, pasta_download):
    caminho_abs = os.path.abspath(pasta_download)
    chrome_options = webdriver.ChromeOptions()
    
    prefs = {
        "download.default_directory": caminho_abs,
        "download.prompt_for_download": False,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window() # Essencial para o PyAutoGUI não errar o alvo
    wait = WebDriverWait(driver, 25)

    try:
        print("🌐 Acessando o site da prefeitura...")
        driver.get("https://saojoao.sc.gov.br")

        print("🖱️ Indo para o Portal do Cidadão...")
        portal = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Portal do Cidadão")))
        driver.execute_script("arguments[0].click();", portal) 

        print("📄 Indo para Certidão Negativa...")
        cnd = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Certidão Negativa")))
        driver.execute_script("arguments[0].click();", cnd)

        # --- LOOP DE PRODUTORES ---
        total_produtores = len(lista_produtores)
        print(f"🚀 Iniciando processamento de {total_produtores} produtores...")

        for index, p in enumerate(lista_produtores):
            sucesso_cpf = False
            tentativas_vaga = 0
            numero_atual = index + 1
            
            while not sucesso_cpf and tentativas_vaga < 3:
                try:
                    if tentativas_vaga == 0:
                        print(f"🚜 [{numero_atual}/{total_produtores}] Processando: {p['nome']}")
                    
                    # 1. Abre o Card de CPF
                    print(f"🖱️ Abrindo o card de CPF...")
                    card_xpath = "//*[contains(text(), 'CPF')]"
                    elemento_card = wait.until(EC.element_to_be_clickable((By.XPATH, card_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento_card)
                    driver.execute_script("arguments[0].click();", elemento_card)
                    time.sleep(3) 

                    # 2. Localiza o ID mainForm:cpf
                    campo_cpf = wait.until(EC.visibility_of_element_located((By.ID, "mainForm:cpf")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_cpf)
                    time.sleep(1)
                    campo_cpf.click() 
                    
                    # 3. Digitação via Hardware
                    print(f"⌨️ PyAutoGUI digitando CPF...")
                    pyautogui.hotkey('ctrl', 'a')
                    pyautogui.press('backspace')
                    pyautogui.write(p["cpf"], interval=0.1)
                    time.sleep(1)
                    pyautogui.press('enter') 
                    
                    # 4. Tela do Contribuinte (Print 2)
                    print("🚀 Carregando lista de contribuintes...")
                    time.sleep(4) 

                    # 4.1. Clique na Impressora
                    print("🖨️ Clicando na impressora...")
                    try:
                        impressora = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "img[src*='print'], a[id*='emitir'], .ui-icon-print")))
                        driver.execute_script("arguments[0].click();", impressora)
                    except:
                        driver.execute_script('document.querySelector("td img[title*=\'Emitir\']").click();')

                    # 4.2. O MOMENTO DO SALVAR (Print 3)
                    print("⏳ Aguardando a CND aparecer na tela...")
                    time.sleep(6) 
                    
                    # 4.2. O MOMENTO DO SALVAR (Print 3)
                    print("⏳ Aguardando a CND aparecer na tela...")
                    time.sleep(7) # Aumentei para 7s para garantir que o PDF carregou
                    
                    print(f"💾 Salvando via Atalho de Teclado (Ctrl+S)...")
                    # Dá um clique no meio da tela para garantir que o foco está no PDF
                    pyautogui.click(driver.get_window_size()['width'] // 2, driver.get_window_size()['height'] // 2)
                    time.sleep(1)
                    
                    # Tenta o atalho universal de salvar
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(2) 
                    
                    # O Windows vai abrir a janelinha de 'Salvar Como'. 
                    # Como o Chrome já está configurado para a pasta certa, só damos Enter.
                    pyautogui.press('enter')
                    print("✅ Comando de salvar enviado!")
                    
                    # 5. MONITOR DE DOWNLOAD
                    print(f"⏳ [{numero_atual}/{total_produtores}] Aguardando arquivo...")
                    arquivo_encontrado = False
                    for segundo in range(30):
                        arquivos = os.listdir(caminho_abs)
                        for arq in arquivos:
                            if arq.lower().endswith(".pdf") and not arq.startswith("CND_"):
                                time.sleep(2) 
                                caminho_antigo = os.path.join(caminho_abs, arq)
                                nome_seguro = p['nome'].replace(" ", "_")
                                novo_nome = f"CND_{nome_seguro}_{p['cpf']}.pdf"
                                os.rename(caminho_antigo, os.path.join(caminho_abs, novo_nome))
                                print(f"💾 SALVO COM SUCESSO: {novo_nome}")
                                arquivo_encontrado = True
                                sucesso_cpf = True
                                break
                        if arquivo_encontrado: break
                        time.sleep(1)

                    # FECHAMENTO DO MODAL
                    print("✖️ Fechando modal...")
                    try:
                        pyautogui.press('esc')
                        time.sleep(2)
                    except:
                        pass
                    
                    # Se salvou ou deu timeout (provável dívida), encerra o loop deste CPF
                    sucesso_cpf = True

                except Exception as e:
                    tentativas_vaga += 1
                    print(f"🔄 Erro na tentativa {tentativas_vaga}: {str(e)[:50]}")
                    driver.get("https://e-gov.betha.com.br/cdweb/03114-192/contribuinte/rel_cndcontribuinte.faces")
                    time.sleep(3)

            # Volta para a tela inicial para o próximo produtor
            driver.get("https://e-gov.betha.com.br/cdweb/03114-192/contribuinte/rel_cndcontribuinte.faces")
            time.sleep(2)

    except Exception as e_global:
        print(f"❌ ERRO CRÍTICO: {e_global}")
    
    finally:
        driver.quit()
        print("🏁 Fim da rodada!")
        
# --- EXECUÇÃO ---
if __name__ == "__main__":
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    pasta_final = os.path.join(diretorio_script, "certidoes_baixadas")
    
    if not os.path.exists(pasta_final): 
        os.makedirs(pasta_final)
    
    pdf_input = os.path.join(diretorio_script, "relatorio_sicas.pdf")
    
    produtores = extrair_dados_sicas(pdf_input)
    if produtores:
        executar_robo_cnd(produtores, pasta_final)