# import requests
# import os
# import time
# from time import sleep

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


# # ---------------------------------------
# # CONFIG
# # ---------------------------------------

# CNPJ = "15070244000118"
# EMAIL = "adm.financeiro@mov.pro.br"

# BASE_API = "https://api-pa-cliente.equatorialenergia.com.br"

# driver = webdriver.Chrome()
# wait = WebDriverWait(driver, 30)


# # ---------------------------------------
# # LOGIN
# # ---------------------------------------

# def fazer_login():

#     driver.get("https://pa.equatorialenergia.com.br/siteantigo/sua-conta/emitir-segunda-via/")

#     # fechar LGPD
#     wait.until(
#         EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'lgpd-btn-close')]"))
#     ).click()

#     # fechar cookies
#     wait.until(
#         EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
#     ).click()

#     # --------------------------------
#     # DIGITAR CNPJ COM LOOP
#     # --------------------------------

#     campo = wait.until(
#         EC.presence_of_element_located((By.ID, "identificador-otp"))
#     )

#     for digito in CNPJ:
#         campo.send_keys(digito)
#         sleep(0.3)

#     botaoEntrar = driver.find_element(By.XPATH, "//button[@id='envia-identificador-otp']")
#     botaoEntrar.click()

#     sleep(3)

#     # --------------------------------
#     # DIGITAR EMAIL COM LOOP
#     # --------------------------------

#     campo_email = wait.until(
#         EC.presence_of_element_located((By.XPATH, "//input[@placeholder='email@empresa.com']"))
#     )

#     for letra in EMAIL:
#         campo_email.send_keys(letra)
#         sleep(0.2)

#     botaoEntrar = driver.find_element(By.XPATH, "//button[@id='envia-identificador']")
#     botaoEntrar.click()

#     time.sleep(5)

#     print("Login realizado")


# # ---------------------------------------
# # CAPTURAR TOKEN
# # ---------------------------------------

# def capturar_token():

#     token = driver.execute_script(
#         "return localStorage.getItem('access_token');"
#     )

#     if not token:
#         token = driver.execute_script(
#             "return sessionStorage.getItem('access_token');"
#         )

#     print("TOKEN CAPTURADO")

#     return token


# # ---------------------------------------
# # LISTAR CONTRATOS
# # ---------------------------------------

# def listar_contratos(token):

#     url = f"{BASE_API}/api/v1/usuario/contas-contrato/{CNPJ}"

#     headers = {
#         "Authorization": f"Bearer {token}"
#     }

#     r = requests.get(url, headers=headers)

#     if r.status_code != 200:
#         print("Erro ao buscar contratos:", r.status_code)
#         return []

#     return r.json()


# # ---------------------------------------
# # CONSULTAR FATURAS
# # ---------------------------------------

# def consultar_faturas(token, contrato):

#     url = f"{BASE_API}/api/v1/debitos/{contrato}?listarEmAberto=false"

#     headers = {
#         "Authorization": f"Bearer {token}"
#     }

#     r = requests.get(url, headers=headers)

#     if r.status_code != 200:
#         print("Erro ao consultar faturas")
#         return []

#     return r.json()


# # ---------------------------------------
# # DOWNLOAD BOLETO
# # ---------------------------------------

# def baixar_boleto(token, contrato, referencia, link):

#     pasta = f"boletos/{contrato}"

#     os.makedirs(pasta, exist_ok=True)

#     nome = referencia.replace("/", "-") + ".pdf"

#     caminho = os.path.join(pasta, nome)

#     headers = {
#         "Authorization": f"Bearer {token}"
#     }

#     r = requests.get(link, headers=headers)

#     if r.status_code == 200:

#         with open(caminho, "wb") as f:
#             f.write(r.content)

#         print("Boleto salvo:", caminho)

#     else:
#         print("Erro download", referencia)


# # ---------------------------------------
# # MAIN
# # ---------------------------------------

# def main():

#     fazer_login()

#     token = capturar_token()

#     print("Buscando contratos...")

#     contratos = listar_contratos(token)

#     print("Total contratos:", len(contratos))

#     for contrato in contratos:

#         numero = contrato["contaContrato"]

#         print("\nContrato:", numero)

#         faturas = consultar_faturas(token, numero)

#         for fatura in faturas:

#             referencia = fatura["referencia"]
#             valor = fatura["valor"]
#             link = fatura["linkBoleto"]

#             print("Fatura:", referencia, "| Valor:", valor)

#             baixar_boleto(token, numero, referencia, link)

#     driver.quit()


# if __name__ == "__main__":
#     main()