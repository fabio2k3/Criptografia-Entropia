import re
import requests
from bs4 import BeautifulSoup

def fetch_guardian_articles(section_url, max_chars=1000000, max_pages=20):
    text = ""
    for page in range(1, max_pages + 1):
        url = f"{section_url}?page={page}"
        print(f"  → Guardian página {page}: leyendo {url}")
        r = requests.get(url)
        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        # Recoge hrefs únicos con fechas en URL
        links = {
            a['href'] if a['href'].startswith("http")
            else "https://www.theguardian.com" + a['href']
            for a in soup.find_all('a', href=True)
            if re.search(r"/\d{4}/[a-z]{3}/\d{2}/", a['href'])
        }
        for link in links:
            if len(text) >= max_chars:
                break
            art = requests.get(link)
            if art.status_code != 200:
                continue
            art_soup = BeautifulSoup(art.text, "html.parser")
            for p in art_soup.select("div[data-gu-name='body'] p"):
                text += p.get_text() + "\n"
                if len(text) >= max_chars:
                    break
        print(f"     acumulado Guardian: {len(text)} caracteres")
        if len(text) >= max_chars:
            break
    return text

if __name__ == "__main__":
    print("Descargando corpus de The Guardian…")
    eng = fetch_guardian_articles(
        "https://www.theguardian.com/world",
        max_chars=1000000,
        max_pages=20
    )
    with open("eng.txt", "w", encoding="utf-8") as f:
        f.write(eng)
    print(f"  ➜ eng.txt: {len(eng)} caracteres")
