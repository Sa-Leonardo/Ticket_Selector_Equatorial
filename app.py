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

digitarEmail = driver.find_element(By.XPATH, "//input[@placeholder='email@empresa.com']")
digitarEmail.send_keys("adm.financeiro@mov.pro.br")
sleep(5)


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

    # Esperar atualizar tabela
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    sleep(3)

    # ---------------------------------------------------------
    #5 - clicar em exibir apenas faturas não pagas
    # ---------------------------------------------------------

    try:
        checkbox = driver.find_element(By.ID, "apenas-vencidas")
        if not checkbox.is_selected():
            checkbox.click()
            sleep(2)
    except:
        pass

    # ---------------------------------------------------------
    #6 - clicar na fatura que aparecer
    # ---------------------------------------------------------

    botoes_ver_fatura = driver.find_elements(By.XPATH, "//tr[contains(., 'default-status em-aberto')]")

    if len(botoes_ver_fatura) == 0:
        print("Nenhuma fatura encontrada")
        return

    print("Faturas encontradas:", len(botoes_ver_fatura))

    for i in range(len(botoes_ver_fatura)):

        # Rebuscar elementos (evita StaleElement)
        botoes_ver_fatura = driver.find_elements(By.XPATH, "//button[contains(., 'Ver fatura')]")

        botoes_ver_fatura[i].click()

        # ---------------------------------------------------------
        #7 - clicar em baixar
        # ---------------------------------------------------------

        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Baixar')]"))
        )

        botao_download = driver.find_element(By.XPATH, "//button[contains(., 'Baixar')]")
        botao_download.click()

        print("Boleto baixado")

        sleep(3)

        driver.back()

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

# =========================================================
# LOOP PRINCIPAL - PERCORRER TODOS CONTRATOS
# =========================================================

for contrato in lista_contratos:
    try:
        processar_contrato(contrato)
    except Exception as e:
        print("⚠ Erro no contrato:", contrato["texto"])
        print("Motivo:", e)

input('')