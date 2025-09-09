from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

# Inicializa el navegador
driver = webdriver.Chrome()  # Asegúrate de tener chromedriver en PATH
driver.get("file:///C:/Users/danim/OneDrive/Documentos/U/Hackaton%20USTA%202025/Despliegue/index.html")  # O la URL donde esté tu formulario

# --- Llenar campos ---
driver.find_element(By.NAME, "documento").send_keys("123456789")

# Edad (slider)
edad_slider = driver.find_element(By.NAME, "edad")
driver.execute_script("arguments[0].value = 35;", edad_slider)
# Actualizar el span mostrado
driver.execute_script("document.getElementById('edad_val').innerText = 35;")

# Documento (slider)
doc_slider = driver.find_element(By.NAME, "doc_publish")
driver.execute_script("arguments[0].value = 3;", doc_slider)
driver.execute_script("document.getElementById('doc_val').innerText = 3;")

# Empleo (slider)
empleo_slider = driver.find_element(By.NAME, "empleo")
driver.execute_script("arguments[0].value = 5;", empleo_slider)
driver.execute_script("document.getElementById('empleo_val').innerText = 5;")

# Celular (slider)
celular_slider = driver.find_element(By.NAME, "celular")
driver.execute_script("arguments[0].value = 12;", celular_slider)
driver.execute_script("document.getElementById('celular_val').innerText = 12;")

# Registro (slider)
registro_slider = driver.find_element(By.NAME, "registro")
driver.execute_script("arguments[0].value = 2;", registro_slider)
driver.execute_script("document.getElementById('registro_val').innerText = 2;")

# Ingresos, crédito, precio, plazo, etc.
driver.find_element(By.NAME, "ingresos").send_keys("1500000")
driver.find_element(By.NAME, "credito").send_keys("5000000")
driver.find_element(By.NAME, "precio").send_keys("4800000")
driver.find_element(By.NAME, "plazo").send_keys("36")
driver.find_element(By.NAME, "area").send_keys("80")

# Región
region_select = Select(driver.find_element(By.NAME, "region"))
region_select.select_by_value("0.05")

# --- Enviar formulario ---
driver.find_element(By.TAG_NAME, "button").click()

# Espera unos segundos para que el backend responda
time.sleep(3)

# (Opcional) capturar resultados
print(driver.page_source)

# Cerrar navegador
driver.quit()
