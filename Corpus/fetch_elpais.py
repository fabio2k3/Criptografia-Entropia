# fetch_elpais_selenium_full.py

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Parámetros
START_URL = "https://elpais.com/ciencia/"
MAX_CHARS = 1_000_000

def setup_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    # evita detección sencilla
    opts.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=opts)

def accept_cookies(driver):
    try:
        # El selector exacto puede variar; intentamos varios
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if any(text in btn.text.lower() for text in ("aceptar", "permitir")):
                btn.click()
                time.sleep(1)
                return
    except Exception:
        pass

def collect_article_links(driver):
    # Scroll lento para cargar elementos
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Ahora extraemos enlaces desde cada <article>
    elems = driver.find_elements(By.CSS_SELECTOR, "article a")
    links = []
    for a in elems:
        href = a.get_attribute("href")
        if href and "/ciencia/" in href and href.startswith("https://elpais.com"):
            links.append(href)
    # Eliminamos duplicados manteniendo orden
    seen = set()
    ordered = []
    for url in links:
        if url not in seen:
            seen.add(url)
            ordered.append(url)
    return ordered

def fetch_elpais_corpus():
    driver = setup_driver()
    driver.get(START_URL)
    time.sleep(2)
    accept_cookies(driver)

    print("🔗 Recopilando enlaces de la sección Ciencia...")
    article_urls = collect_article_links(driver)
    print(f"  → {len(article_urls)} artículos encontrados.\n")

    text = ""
    for idx, url in enumerate(article_urls, start=1):
        if len(text) >= MAX_CHARS:
            break
        print(f"📥 [{idx}/{len(article_urls)}] Abriendo {url}")
        driver.get(url)
        time.sleep(1)
        paras = driver.find_elements(By.CSS_SELECTOR, "article p")
        for p in paras:
            text += p.text + "\n"
            if len(text) >= MAX_CHARS:
                break
        print(f"   → Acumulado: {len(text):,} caracteres\n")

    driver.quit()
    return text

if __name__ == "__main__":
    print("🔎 Empezando descarga de El País (Selenium)...")
    corpus = fetch_elpais_corpus()
    with open("esp.txt", "w", encoding="utf-8") as f:
        f.write(corpus)
    print(f"\n✅ esp.txt generado con {len(corpus):,} caracteres")
