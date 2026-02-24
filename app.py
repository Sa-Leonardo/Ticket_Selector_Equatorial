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
from time import sleep

driver = webdriver.Chrome()

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




input('')