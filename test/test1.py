from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os

# =========================================================
# CONFIGURAÇÃO DO DRIVER
# =========================================================

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

PASTA_DOWNLOAD = os.path.join(os.getcwd(), "faturas_pdf")
os.makedirs(PASTA_DOWNLOAD, exist_ok=True)

prefs = {
    "download.default_directory": PASTA_DOWNLOAD,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True,
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)

# =========================================================
# CONSTANTES
# =========================================================

CNPJ  = "15070244000118"
EMAIL = "adm.financeiro@mov.pro.br"
URL   = "https://pa.equatorialenergia.com.br/siteantigo/sua-conta/emitir-segunda-via/"

# =========================================================
# ACESSO AO SITE
# =========================================================

driver.get(URL)
sleep(3)

# 1.1 - Fechar LGPD
try:
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class,'lgpd-btn-close')]")
    )).click()
    sleep(1)
except Exception as e:
    print("⚠️ Botão LGPD não encontrado:", e)

# 1.2 - Fechar cookies
try:
    wait.until(EC.element_to_be_clickable(
        (By.ID, "onetrust-reject-all-handler")
    )).click()
    sleep(1)
except Exception as e:
    print("⚠️ Botão de cookies não encontrado:", e)

# =========================================================
# LOGIN - CNPJ
# =========================================================

campo_cnpj = wait.until(EC.presence_of_element_located((By.ID, "identificador-otp")))
for digito in CNPJ:
    campo_cnpj.send_keys(digito)
    sleep(0.2)

wait.until(EC.element_to_be_clickable((By.ID, "envia-identificador-otp"))).click()
sleep(3)

# =========================================================
# LOGIN - EMAIL
# =========================================================

campo_email = wait.until(EC.presence_of_element_located(
    (By.XPATH, "//input[@placeholder='email@empresa.com']")
))
for letra in EMAIL:
    campo_email.send_keys(letra)
    sleep(0.15)

wait.until(EC.element_to_be_clickable((By.ID, "envia-identificador"))).click()
sleep(3)

# =========================================================
# CARREGAR LISTA DE CONTRATOS
# =========================================================

wait.until(EC.presence_of_element_located((By.ID, "conta_contrato")))
wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#conta_contrato option")) > 1)

options = driver.find_elements(By.CSS_SELECTOR, "#conta_contrato option")
print(f"Opções encontradas: {len(options)}")

lista_contratos = []
for option in options:
    texto = option.text.strip()
    valor = option.get_attribute("value")
    if valor and texto:
        lista_contratos.append({"texto": texto, "value": valor})

print("Contratos:", lista_contratos)

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def salvar_codigo(contrato, codigo, referencia, vencimento, valor):
    with open("codigos.txt", "a", encoding="utf-8") as f:
        f.write(
            f"Contrato: {contrato} | "
            f"Referência: {referencia} | "
            f"Vencimento: {vencimento} | "
            f"Valor: {valor} | "
            f"Código: {codigo}\n"
        )
    print(f"💾 Código salvo — Contrato: {contrato}")


# =========================================================
# FUNÇÃO PRINCIPAL - PROCESSAR CADA CONTRATO
# =========================================================

def processar_contrato(contrato):
    print(f"\n{'='*50}")
    print(f"🔄 Processando: {contrato['texto']}")

    # Selecionar contrato no dropdown
    select_element = wait.until(EC.presence_of_element_located((By.ID, "conta_contrato")))
    Select(select_element).select_by_value(contrato["value"])

    # Aguardar tabela carregar
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    sleep(3)

    # ---------------------------------------------------------
    # 5 - Marcar checkbox "exibir apenas faturas não pagas"
    # ---------------------------------------------------------

    try:
        checkbox = wait.until(EC.presence_of_element_located((By.ID, "apenas-vencidas")))

        # Rolar até o checkbox para garantir visibilidade
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
        sleep(1)

        # Clicar apenas se ainda NÃO estiver marcado
        if not checkbox.is_selected():
            print("☑️ Marcando checkbox 'apenas faturas não pagas'...")
            driver.execute_script("arguments[0].click();", checkbox)
            sleep(3)
        else:
            print("✅ Checkbox já estava marcado.")

        # Segunda verificação — se ainda não marcou, tenta de novo
        if not checkbox.is_selected():
            print("⚠️ Checkbox não marcou, tentando novamente...")
            driver.execute_script("arguments[0].click();", checkbox)
            sleep(3)

    except Exception as e:
        print(f"⚠️ Erro no checkbox: {e}")

    # Aguardar tabela estabilizar após o filtro
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    sleep(2)

    # ---------------------------------------------------------
    # 6 - Buscar faturas em aberto
    #
    # HTML real da fatura:
    # <tr class="default-status em-aberto"
    #     data-codigo-pagamento="836700000026011..."
    #     data-numero-fatura="311506574473">
    #   <td class="bill-reference">
    #     <span class="referencia_legada">03/2026</span>
    #   </td>
    #   <td class="bill-value">R$ 201,10</td>
    #   <td class="bill-date"><span>Vencimento</span><br> 19/03/2026</td>
    # </tr>
    #
    # O código de barras já está no atributo data-codigo-pagamento!
    # Não precisa clicar em nada para obtê-lo.
    # ---------------------------------------------------------

    faturas = driver.find_elements(By.XPATH, "//tr[contains(@class,'em-aberto')]")

    if not faturas:
        print("ℹ️ Nenhuma fatura em aberto. Passando para o próximo contrato...")
        return

    print(f"📋 {len(faturas)} fatura(s) em aberto encontrada(s).")

    for fatura in faturas:
        try:
            referencia = fatura.find_element(By.CLASS_NAME, "referencia_legada").text.strip()
            vencimento = fatura.find_element(By.CLASS_NAME, "bill-date").text.split("\n")[-1].strip()
            valor      = fatura.find_element(By.CLASS_NAME, "bill-value").text.strip()
            codigo     = fatura.get_attribute("data-codigo-pagamento")

            print(f"📄 {referencia} | Venc: {vencimento} | Valor: {valor}")

            if not codigo:
                print("⚠️ Código de barras vazio, pulando esta fatura...")
                continue

            print(f"📌 Código: {codigo}")
            salvar_codigo(contrato["texto"], codigo, referencia, vencimento, valor)

            break  # Pega apenas a primeira fatura em aberto por contrato

        except Exception as e:
            print(f"❌ Erro ao ler fatura: {e}")

# =========================================================
# LOOP PRINCIPAL
# =========================================================

for contrato in lista_contratos:
    try:
        processar_contrato(contrato)
    except Exception as e:
        print(f"\n❌ Erro no contrato '{contrato['texto']}': {e}")

print("\n✅ Processamento finalizado!")
input("Pressione Enter para fechar o navegador...")
driver.quit()