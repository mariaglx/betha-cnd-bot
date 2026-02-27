import pdfplumber
import PyPDF2 # Importante para a análise de conteúdo
import re
import time
import os
import pyautogui
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- CONSTANTES GLOBAIS (Busca do .env) ---
ARQUIVO_PDF_FONTE = os.getenv("ARQUIVO_FONTE")
SITE_INICIAL = os.getenv("SITE_PREFEITURA")
PASTA_DESTINO = os.getenv("DOWNLOAD_CERTIDAO")
URL_RESETA_SISTEMA = os.getenv("URL_BETHA_SISTEMA")

# --- PARTE 1: EXTRAÇÃO ---
def extrair_dados_sicas(caminho_pdf):
    print(f"🔍 Lendo Relatório: {ARQUIVO_PDF_FONTE}...")
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
    lista_final = [d for d in dados if not (d['cpf'] in vistos or vistos.add(d['cpf']))]
    print(f"✅ {len(lista_final)} produtores encontrados.")
    return lista_final

# --- PARTE 2: ROBÔ ---
def executar_robo_cnd(lista_produtores, pasta_download):
    caminho_abs = os.path.abspath(pasta_download)
    chrome_options = webdriver.ChromeOptions()
    
    prefs = {
        "download.default_directory": caminho_abs,
        "download.prompt_for_download": False,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "pdfjs.disabled": True # Força o download em vez de visualização
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 25)

    try:
        print(f"🌐 Acessando: {SITE_INICIAL}")
        driver.get(SITE_INICIAL)

        print("🖱️ Navegando até o portal Betha...")
        portal = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Portal do Cidadão")))
        driver.execute_script("arguments[0].click();", portal) 

        cnd = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Certidão Negativa")))
        driver.execute_script("arguments[0].click();", cnd)

        total_produtores = len(lista_produtores)
        for index, p in enumerate(lista_produtores):
            sucesso_cpf = False
            tentativas = 0
            numero_atual = index + 1
            
            while not sucesso_cpf and tentativas < 3:
                try:
                    print(f"🚜 [{numero_atual}/{total_produtores}] Processando: {p['nome']}")
                    
                    # 1. Seleção de CPF
                    card_xpath = "//*[contains(text(), 'CPF')]"
                    elemento_card = wait.until(EC.element_to_be_clickable((By.XPATH, card_xpath)))
                    driver.execute_script("arguments[0].click();", elemento_card)
                    time.sleep(3) 

                    # 2. Preenchimento
                    campo_cpf = wait.until(EC.visibility_of_element_located((By.ID, "mainForm:cpf")))
                    campo_cpf.click()
                    pyautogui.hotkey('ctrl', 'a')
                    pyautogui.press('backspace')
                    pyautogui.write(p["cpf"], interval=0.1)
                    pyautogui.press('enter')
                    time.sleep(4) 

                    # 3. Emissão (Impressora)
                    print("🖨️ Emitindo...")
                    try:
                        impressora = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "img[src*='print'], .ui-icon-print")))
                        driver.execute_script("arguments[0].click();", impressora)
                    except:
                        driver.execute_script('document.querySelector("td img[title*=\'Emitir\']").click();')

                    # 4. Salvamento (Bypass de Modal)
                    print("💾 Salvando via Hardware...")
                    time.sleep(7) 
                    pyautogui.click(driver.get_window_size()['width'] // 2, driver.get_window_size()['height'] // 2)
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(2)
                    pyautogui.press('enter')
                    
                    # 5. Monitoramento e Análise de Conteúdo (Negativa vs Positiva)
                    arquivo_encontrado = False
                    for _ in range(30):
                        arquivos = os.listdir(caminho_abs)
                        for arq in arquivos:
                            if arq.lower().endswith(".pdf") and not arq.startswith("CND_"):
                                time.sleep(2)
                                caminho_antigo = os.path.join(caminho_abs, arq)
                                
                                # --- ANÁLISE DO PDF ---
                                status_final = "REVISAR"
                                try:
                                    with open(caminho_antigo, 'rb') as f:
                                        leitor = PyPDF2.PdfReader(f)
                                        texto_extraido = leitor.pages[0].extract_text()
                                        
                                        if "Sem débitos pendentes" in texto_extraido:
                                            status_final = "NEGATIVA"
                                            print(f"🟢 {p['nome']}: NEGATIVA.")
                                        elif "Com débitos pendentes" in texto_extraido:
                                            status_final = "POSITIVA"
                                            print(f"🔴 {p['nome']}: POSITIVA.")
                                except: pass

                                novo_nome = f"CND_{status_final}_{p['nome'].replace(' ', '_')}_{p['cpf']}.pdf"
                                os.rename(caminho_antigo, os.path.join(caminho_abs, novo_nome))
                                arquivo_encontrado = True
                                sucesso_cpf = True
                                break
                        if arquivo_encontrado: break
                        time.sleep(1)

                    pyautogui.press('esc')
                    sucesso_cpf = True

                except Exception as e:
                    tentativas += 1
                    driver.get(URL_RESETA_SISTEMA)
                    time.sleep(3)

            driver.get(URL_RESETA_SISTEMA)
            time.sleep(2)

    finally:
        driver.quit()
        print("🏁 Fim da rodada!")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Usa a pasta do .env ou cria uma padrão no desktop do script
    pasta_final = PASTA_DESTINO or os.path.join(diretorio_atual, "certidoes_baixadas")
    if not os.path.exists(pasta_final): os.makedirs(pasta_final)
    
    caminho_pdf = os.path.join(diretorio_atual, ARQUIVO_PDF_FONTE)
    
    produtores = extrair_dados_sicas(caminho_pdf)
    if produtores:
        executar_robo_cnd(produtores, pasta_final)