import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import requests
from dotenv import load_dotenv #Importem la funció per carregar .env

load_dotenv() 
# CONFIGURACIÓN TELEGRAM
TELEGRAM_TOKEN = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = os.getenv("CHAT_ID")



URL = "https://www.normacomics.com/all-products?libros_serie=35235"
DATA_FILE = "llibres_vistos.json"

def enviar_telegram(missatge):
    url_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": missatge,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url_api, data=payload)
    except Exception as e:
        print(f"Error enviant a Telegram: {e}")

def carregar_vistos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def guardar_vistos(llibres):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(llibres, f, ensure_ascii=False, indent=4)

def consultar_i_comparar():
    driver = None
    try:
        print("Iniciant navegador...")
        options = uc.ChromeOptions()
        # Mantenim el mode visible per evitar bloquejos de Cloudflare
        options.add_argument('--start-maximized')
        
        driver = uc.Chrome(options=options, version_main=146)
        
        print("Obrent la web i esperant seguretat...")
        driver.get(URL)
        time.sleep(10) # Temps per a la validació de Cloudflare

        wait = WebDriverWait(driver, 20)
        elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-item-link")))
        
        llibres_actuals = sorted(list(set([el.get_attribute('innerText').strip() for el in elements if el.get_attribute('innerText').strip()])))

        if not llibres_actuals:
            print("No s'han trobat llibres.")
            return

        vistos = carregar_vistos()
        nous = [l for l in llibres_actuals if l not in vistos]
        
        if nous:
            text_telegram = "<b>🔔 ¡NOVES TROBALLES A NORMA!</b>\n\n"
            for n in nous:
                text_telegram += f"• {n}\n"
            text_telegram += f"\nLink: <a href='{URL}'>Veure a la web</a>"
            
            print("Enviant notificació a Telegram...")
            enviar_telegram(text_telegram)
            guardar_vistos(llibres_actuals)
        else:
            print("No hi ha novetats.")

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if driver:
            time.sleep(2)
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    consultar_i_comparar()