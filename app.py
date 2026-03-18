#1 - abrir o site - https://pa.equatorialenergia.com.br/siteantigo/sua-conta/emitir-segunda-via/

#1.1 - fechar aba de LGPD

#2 - clicar em cpf/cnpj

#3 - Digitar CNPJ principal

#4 - Clicar no campo de digitar email (serve como senha)

#5 - clicar em exibir apenas faturas não pagas

#6 - Clicar na fatura que aparecer

#7 - clicar em copiar código de barras ou clicar em ver fatura
	#se clicar em ver fatura
		#clicar em baixar e armazenar em um local
	#senão se clicar em copiar código de barras
		#armazenar em outro local


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from time import sleep
from datetime import datetime

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 30)


driver.get('https://pa.equatorialenergia.com.br/siteantigo/sua-conta/emitir-segunda-via/')

#1.1 - fechar aba de LGPD

#Para selecionar o XPATH(identificador de elementos em um site)  -  //tag[@atributo='valor']

botaolgpd = driver.find_element(By.XPATH, "//button[contains(@class,'lgpd-btn-close')]")
botaolgpd.click()

#1.1 - fechar aba de cookies

botaoCookie = driver.find_element(By.XPATH, "//button[@id='onetrust-reject-all-handler']")
botaoCookie.click()

#2 - clicar em cpf/cnpj

cnpj = "15070244000118"
campo = driver.find_element(By.ID, "identificador-otp")

#3 - Digitar CNPJ principal

for digito in cnpj:
    campo.send_keys(digito)
    sleep(0.3)  # ajuste 0.05 ~ 0.3

botaoEntrar = driver.find_element(By.XPATH, "//button[@id='envia-identificador-otp']")
botaoEntrar.click()
sleep(3)

#4 - Clicar no campo de digitar email (serve como senha)

email = "adm.financeiro@mov.pro.br"

campo_email = driver.find_element(By.XPATH, "//input[@placeholder='email@empresa.com']")

for letra in email:
    campo_email.send_keys(letra)
    sleep(0.2)


botaoEntrar = driver.find_element(By.XPATH, "//button[@id='envia-identificador']")
botaoEntrar.click()


#fazer a verificação de cada conta contrato

wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#conta_contrato option")) > 0)

options = driver.find_elements(By.CSS_SELECTOR, "#conta_contrato option")

print("Quantidade de options encontradas:", len(options))

lista_contratos = []

for option in options:
    texto = option.text.strip()
    valor = option.get_attribute("value")

    if valor:
        lista_contratos.append({
            "texto": texto,
            "value": valor
        })

print("Lista final:", lista_contratos)

# =========================================================
# FUNÇÃO PARA PROCESSAR CADA CONTRATO
# =========================================================

def processar_contrato(contrato):

    print("Processando contrato:", contrato["texto"])

    # Sempre recriar o Select
    select = Select(driver.find_element(By.ID, "conta_contrato"))
    select.select_by_value(contrato["value"])
    sleep(5)

    # Esperar atualizar tabela
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    sleep(8)

    # ---------------------------------------------------------
    #5 - clicar em exibir apenas faturas não pagas
    # ---------------------------------------------------------


    checkbox = driver.find_element(By.ID, "apenas-vencidas")
    checkbox.click()

    # try:
    #     checkbox = driver.find_element(By.ID, "apenas-vencidas")
    #     if not checkbox.is_selected():
    #         checkbox.click()
    #         sleep(2)
    # except:
    #     pass

    # ---------------------------------------------------------
    #6 - clicar na fatura que aparecer
    # ---------------------------------------------------------

        # pegar faturas em aberto
    faturas = driver.find_elements(By.CSS_SELECTOR, "tr.default-status.em-aberto")

    if not faturas:
        print("Nenhuma fatura encontrada")
        return

    mes_atual = datetime.now().strftime("%m/%Y")

    for fatura in faturas:

        try:
            referencia = fatura.find_element(By.CLASS_NAME, "referencia_legada").text.strip()
            vencimento = fatura.find_element(By.CLASS_NAME, "bill-date").text.split("\n")[-1].strip()

            print(f"📄 {referencia} | {vencimento}")

            # validar mês atual
            if referencia != mes_atual:
                continue

            print("✅ - Fatura do mês atual encontrada")

            # clicar na linha
            driver.execute_script("arguments[0].click();", fatura)

            # esperar botões aparecerem
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'copy-code-button')]")))

            sleep(5)

            # tentar copiar código de barras
            try:
                botao_copiar = driver.find_element(By.XPATH, "//a[contains(@class,'copy-code-button')]")
                botao_copiar.click()

                sleep(4)

                codigo = driver.execute_script("return navigator.clipboard.readText();")

                salvar_codigo(contrato["texto"], codigo, vencimento)

                print("📌 Código de barras salvo")

            except Exception as e:
                print("⚠️ Não conseguiu copiar, tentando baixar PDF")

                # clicar em ver fatura
                botao_ver = driver.find_element(By.XPATH, "//button[contains(., 'Ver fatura')]")
                botao_ver.click()

                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Baixar')]")))

                botao_download = driver.find_element(By.XPATH, "//button[contains(., 'Baixar')]")
                botao_download.click()

                print("📥 PDF baixado")

                salvar_log_pdf(contrato["texto"], vencimento)

                sleep(3)

            break  # só pega 1 fatura por contrato

        except Exception as e:
            print("Erro na fatura:", e)

# =========================================================
# SALVAR DADOS DO CONTRATO E CÓDIGO DE BARRAS
# =========================================================           


def salvar_codigo(contrato, codigo, vencimento):
    with open("codigos.txt", "a", encoding="utf-8") as f:
        f.write(f"Contrato: {contrato} | Código: {codigo} | Vencimento: {vencimento}\n")


def salvar_log_pdf(contrato, vencimento):
    with open("pdfs.txt", "a", encoding="utf-8") as f:
        f.write(f"Contrato: {contrato} | PDF baixado | Vencimento: {vencimento}\n")

# =========================================================
# LOOP PRINCIPAL - PERCORRER TODOS CONTRATOS
# =========================================================

for contrato in lista_contratos:
    try:
        processar_contrato(contrato)
    except Exception as e:
        print("Erro no contrato:", contrato["texto"])
        print("Motivo:", e)

input('')