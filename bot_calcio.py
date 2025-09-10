import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot
import logging
import re
import os
import ssl
import urllib.parse
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- CONFIG ---
TELEGRAM_TOKEN = "8117577193:AAHnfVWVsgQ1a_8dqeJ5eMnQs1LQ9RAUrTA"
CHAT_ID = "69684347"
SEEN_MATCHES_FILE = "seen_matches.txt"
SEEN_ARTICLES_FILE = "seen_articles.txt"

# ✅ MAPPA NAZIONE (in qualsiasi lingua) → LINGUA (per keyword) — NOMI DELLE NAZIONI IN ITALIANO
NATION_TO_LANG = {
    # Europa
    "Italia": "it",
    "Inghilterra": "en",
    "Germania": "de",
    "Francia": "fr",
    "Spagna": "es",
    "Portogallo": "pt",
    "Olanda": "nl",
    "Belgio": "nl",
    "Scozia": "en",
    "Grecia": "el",
    "Turchia": "tr",
    "Russia": "ru",
    "Ucraina": "uk",
    "Svizzera": "de",
    "Austria": "de",
    "Danimarca": "da",
    "Svezia": "sv",
    "Norvegia": "no",
    "Finlandia": "fi",
    "Irlanda": "en",
    "Galles": "en",
    "Repubblica Ceca": "cs",
    "Slovacchia": "sk",
    "Ungheria": "hu",
    "Polonia": "pl",
    "Romania": "ro",
    "Bulgaria": "bg",
    "Serbia": "sr",
    "Croazia": "hr",
    "Slovenia": "sl",
    "Bosnia": "bs",
    "Montenegro": "sr",
    "Albania": "sq",
    "Macedonia": "mk",
    "Kosovo": "sq",
    "Islanda": "is",
    "Lituania": "lt",
    "Lettonia": "lv",
    "Estonia": "et",
    "Bielorussia": "be",
    "Moldavia": "ro",
    "Andorra": "ca",
    "Liechtenstein": "de",
    "Malta": "mt",
    "Cipro": "el",
    "San Marino": "it",
    "Vaticano": "it",
    "Monaco": "fr",

    # Sud America
    "Argentina": "es",
    "Brasile": "pt",
    "Cile": "es",
    "Uruguay": "es",
    "Paraguay": "es",
    "Bolivia": "es",
    "Perù": "es",
    "Ecuador": "es",
    "Colombia": "es",
    "Venezuela": "es",
    "Guyana": "en",
    "Suriname": "nl",
    "Guyana Francese": "fr",

    # Nord/Centro America
    "Stati Uniti": "en",
    "Canada": "en",
    "Messico": "es",
    "Costa Rica": "es",
    "Honduras": "es",
    "Nicaragua": "es",
    "El Salvador": "es",
    "Guatemala": "es",
    "Panama": "es",
    "Cuba": "es",
    "Giamaica": "en",
    "Trinidad e Tobago": "en",
    "Curacao": "en",
    "Bermuda": "en",
    "Haiti": "fr",
    "Repubblica Dominicana": "es",
    "Bahamas": "en",
    "Barbados": "en",
    "Antigua e Barbuda": "en",
    "Saint Kitts e Nevis": "en",
    "Dominica": "en",
    "Saint Lucia": "en",
    "Saint Vincent e Grenadine": "en",
    "Grenada": "en",

    # Africa
    "Sudafrica": "en",
    "Egitto": "ar",
    "Nigeria": "en",
    "Ghana": "en",
    "Senegal": "fr",
    "Marocco": "ar",
    "Algeria": "ar",
    "Tunisia": "ar",
    "Camerun": "fr",
    "Costa d'Avorio": "fr",
    "Mali": "fr",
    "Burkina Faso": "fr",
    "Congo": "fr",
    "RD Congo": "fr",
    "Angola": "pt",
    "Mozambico": "pt",
    "Zambia": "en",
    "Zimbabwe": "en",
    "Kenya": "en",
    "Uganda": "en",
    "Tanzania": "sw",
    "Etiopia": "am",
    "Sudan": "ar",
    "Sudan del Sud": "en",
    "Libia": "ar",
    "Eritrea": "ti",
    "Somalia": "so",
    "Djibouti": "fr",
    "Ruanda": "rw",
    "Burundi": "fr",
    "Gabon": "fr",
    "Guinea Equatoriale": "es",
    "São Tomé e Príncipe": "pt",
    "Capo Verde": "pt",
    "Guinea-Bissau": "pt",
    "Sierra Leone": "en",
    "Liberia": "en",
    "Togo": "fr",
    "Benin": "fr",
    "Niger": "fr",
    "Ciad": "fr",
    "Mauritania": "ar",
    "Maurizio": "en",
    "Seychelles": "fr",
    "Comore": "ar",
    "Madagascar": "mg",
    "Namibia": "en",
    "Botswana": "en",
    "Lesotho": "en",
    "Swaziland": "en",
    "Gambia": "en",
    "Guinea": "fr",

    # Asia
    "Indonesia": "id",
    "Giappone": "ja",
    "Corea del Sud": "ko",
    "Cina": "zh",
    "India": "hi",
    "Arabia Saudita": "ar",
    "Iran": "fa",
    "Iraq": "ar",
    "Israele": "he",
    "Giordania": "ar",
    "Libano": "ar",
    "Siria": "ar",
    "Palestina": "ar",
    "Yemen": "ar",
    "Oman": "ar",
    "Emirati Arabi Uniti": "ar",
    "Qatar": "ar",
    "Kuwait": "ar",
    "Bahrain": "ar",
    "Turchia": "tr",
    "Cipro": "el",
    "Georgia": "ka",
    "Armenia": "hy",
    "Azerbaigian": "az",
    "Kazakistan": "kk",
    "Uzbekistan": "uz",
    "Tagikistan": "tg",
    "Kirghizistan": "ky",
    "Turkmenistan": "tk",
    "Afghanistan": "ps",
    "Pakistan": "ur",
    "Bangladesh": "bn",
    "Sri Lanka": "si",
    "Nepal": "ne",
    "Bhutan": "dz",
    "Maldive": "dv",
    "Myanmar": "my",
    "Thailandia": "th",
    "Laos": "lo",
    "Cambogia": "km",
    "Vietnam": "vi",
    "Filippine": "tl",
    "Malesia": "ms",
    "Singapore": "en",
    "Brunei": "ms",
    "Timor Est": "pt",
    "Taiwan": "zh",
    "Hong Kong": "zh",
    "Macao": "zh",
    "Mongolia": "mn",
    "Corea del Nord": "ko",

    # Oceania
    "Australia": "en",
    "Nuova Zelanda": "en",
    "Fiji": "en",
    "Papua Nuova Guinea": "en",
    "Isole Salomone": "en",
    "Vanuatu": "bi",
    "Samoa": "sm",
    "Tonga": "to",
    "Kiribati": "en",
    "Tuvalu": "en",
    "Nauru": "en",
    "Palau": "en",
    "Micronesia": "en",
    "Marshall": "en",
    "Nuova Caledonia": "fr",
    "Polinesia Francese": "fr",
    "Wallis e Futuna": "fr",
    "Samoa Americane": "en",
    "Guam": "en",
    "Isole Marianne Settentrionali": "en",
    "Isole Cook": "en",
    "Niue": "en",
    "Tokelau": "en",
    "Pitcairn": "en",
}

# Keyword per lingua
KEYWORDS_BY_LANG = {
    "it": [
        "formazione alternativa", "formazione rimaneggiata", "squadra decimata", "tanti assenti",
        "titolari assenti", "stipendi non pagati", "allenatore esonerato", "protesta", "sciopero",
        "rosa ridotta", "gravi difficoltà", "crisi squadra"
    ],
    "en": [
        "emergency lineup", "squad decimated", "many absentees",
        "starting eleven missing", "salaries not paid", "coach fired", "coach sacked", "strike",
        "team in crisis", "players boycott"
    ],
    "de": [
        "alternative Aufstellung", "Notaufstellung", "Mannschaft dezimiert", "viele Ausfälle",
        "Stammspieler fehlen", "Löhne nicht gezahlt", "Trainer entlassen", "Streik",
        "Krise im Team", "Mannschaft reduziert"
    ],
    "es": [
        "alineación alternativa", "alineación de emergencia", "equipo diezmado", "muchas bajas",
        "once titular ausente", "sueldos no pagados", "entrenador despedido", "huelga",
        "equipo en crisis", "jugadores boicotean"
    ],
    "pt": [
        "escalação alternativa", "escalação emergencial", "equipe desfalcada", "muitas ausências",
        "titulares ausentes", "salários não pagos", "treinador demitido", "greve",
        "equipe em crise", "jogadores boicoteiam"
    ],
    "id": [
        "susunan pemain alternatif", "pemain absen", "tim dipangkas", "banyak pemain absen",
        "gaji tidak dibayar", "pelatih dipecat", "pemogokan", "tim dalam krisis",
        "pemain inti absen", "protes terhadap klub"
    ]
}

# Carica partite/articoli già visti
def load_seen(file):
    if not os.path.exists(file):
        return set()
    with open(file, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(file, item):
    with open(file, "a", encoding="utf-8") as f:
        f.write(item.strip() + "\n")

seen_matches = load_seen(SEEN_MATCHES_FILE)
seen_articles = load_seen(SEEN_ARTICLES_FILE)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Disabilita SSL
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def send_telegram(titolo, link, motivo, lang, snippet, bot):
    msg = f"⚠️ ALERT PARTITA OGGI [{lang.upper()}]\n⚽ {titolo}\n🔍 Motivo: {motivo}\n🔗 {link}\n\n📝 {snippet[:200]}..."
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        logging.info(f"Inviato alert per: {titolo}")
        await asyncio.sleep(1)
    except Exception as e:
        logging.error(f"Errore Telegram: {e}")

# Estrae testo da un URL (fallback)
async def extract_text(session, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with session.get(url, headers=headers, timeout=15) as resp:
            if resp.status != 200:
                return ""
            html = await resp.text(errors='ignore')
            soup = BeautifulSoup(html, "html.parser")
            for selector in ["article", ".entry-content", "main p", "p"]:
                texts = [p.get_text(" ", strip=True) for p in soup.select(selector) if len(p.get_text()) > 50]
                if texts:
                    return " ".join(texts)[:5000]
            return ""
    except Exception as e:
        logging.warning(f"Errore estrazione {url}: {e}")
        return ""

# ✅ CERCA SU GOOGLE CON SELENIUM (EVITA BLOCCHI)
def google_search_with_selenium(query):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    results = []
    try:
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=10"
        driver.get(search_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)

        g_containers = driver.find_elements(By.CSS_SELECTOR, "div.g")
        for g in g_containers[:5]:
            try:
                link_elem = g.find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute("href")
                if not link or "google.com" in link:
                    continue

                title_elem = g.find_element(By.TAG_NAME, "h3")
                title = title_elem.text if title_elem else "No title"

                results.append({'title': title, 'link': link})
                logging.info(f"✅ Google risultato trovato: {title[:50]}...")

            except Exception as e:
                continue

    except Exception as e:
        logging.warning(f"Errore ricerca Google con Selenium: {e}")
    finally:
        driver.quit()

    return results

# ✅ ESTRARRE PARTITE DA DIRETTA.IT — USA SOLO LA NAZIONE DAL TESTO IN GRASSETTO
def get_matches_from_diretta_with_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=options)
    matches = []
    try:
        driver.get("https://www.diretta.it/")
        logging.info("Caricamento pagina diretta.it...")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "event__match"))
        )

        # Scrolla per caricare tutte le partite
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # ✅ TROVA TUTTI I BLOCCHI "NAZIONE" (GRASSETTO)
        nation_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'event__title--name')]/strong")

        for nation_block in nation_blocks:
            try:
                nation_text = nation_block.text.strip()
                if not nation_text or len(nation_text) < 2:
                    continue

                logging.info(f"🔍 Trovata nazione: {nation_text}")

                # ✅ TROVA TUTTE LE PARTITE SOTTO QUESTO BLOCCO
                parent_container = nation_block.find_element(By.XPATH, "./ancestor::*[contains(@class, 'event__header')]")
                if not parent_container:
                    continue

                following_matches = parent_container.find_elements(By.XPATH, "./following-sibling::*[contains(@class, 'event__match')]")

                for event in following_matches:
                    try:
                        if event.get_attribute("class") and "event__header" in event.get_attribute("class"):
                            break

                        # Estrai ora
                        match_time = "N/A"
                        try:
                            time_elem = event.find_element(By.CLASS_NAME, "event__time")
                            match_time = time_elem.text.strip()
                        except:
                            pass

                        # Estrai squadre
                        home_team = "N/A"
                        away_team = "N/A"
                        try:
                            home_elem = event.find_element(By.CLASS_NAME, "event__participant--home")
                            away_elem = event.find_element(By.CLASS_NAME, "event__participant--away")
                            home_team = home_elem.text.strip()
                            away_team = away_elem.text.strip()
                        except:
                            try:
                                participants = event.find_elements(By.XPATH, ".//*[contains(@class, 'participant')]")
                                if len(participants) >= 2:
                                    home_team = participants[0].text.strip()
                                    away_team = participants[-1].text.strip()
                            except:
                                pass

                        if home_team == "N/A" or away_team == "N/A" or len(home_team) < 2 or len(away_team) < 2:
                            continue

                        teams = f"{home_team} - {away_team}"

                        # ✅ USA LA NAZIONE TROVATA (in italiano)
                        nation = nation_text
                        lang = "en"
                        for pattern, lang_code in NATION_TO_LANG.items():
                            if pattern.lower() in nation.lower():
                                lang = lang_code
                                break

                        match_key = f"{teams} | {nation} | {match_time}"

                        if match_key not in seen_matches:
                            matches.append({
                                'teams': teams,
                                'nation': nation,
                                'lang': lang,
                                'time': match_time,
                                'key': match_key
                            })
                            seen_matches.add(match_key)
                            save_seen(SEEN_MATCHES_FILE, match_key)
                            logging.info(f"✅ Nuova partita estratta: {teams} ({nation}) - {match_time} | Lingua: {lang}")

                    except Exception as e:
                        logging.warning(f"Errore parsing partita sotto {nation_text}: {e}")
                        continue

            except Exception as e:
                logging.warning(f"Errore parsing blocco nazione: {e}")
                continue

    except Exception as e:
        logging.error(f"Errore scraping diretta.it con Selenium: {e}")
    finally:
        driver.quit()

    return matches

# ✅ PROCESSA OGNI PARTITA: CERCA SU GOOGLE + INVIA SU TELEGRAM
async def process_match(session, match, bot):
    teams = match['teams']
    lang = match['lang']

    keywords = KEYWORDS_BY_LANG.get(lang, KEYWORDS_BY_LANG["en"])

    logging.info(f"Processando: {teams} | Lingua: {lang}")

    for keyword in keywords:
        query = f'"{teams}" "{keyword}"'
        logging.info(f"Cerco su Google: {query}")

        # ✅ USA SELENIUM PER GOOGLE
        results = google_search_with_selenium(query)

        for result in results[:3]:
            link = result['link']
            title = result['title']

            if link in seen_articles:
                continue

            # Estrai testo articolo (fallback)
            text = await extract_text(session, link)
            found_keyword = None
            search_text = (text + " " + title).lower()
            for kw in keywords:
                if kw.lower() in search_text:
                    found_keyword = kw
                    break

            if found_keyword:
                await send_telegram(teams, link, found_keyword, lang, text, bot)
                seen_articles.add(link)
                save_seen(SEEN_ARTICLES_FILE, link)
                logging.info(f"✅ Trovato match: {teams} | {found_keyword} ({lang})")

            time.sleep(1)  # Pausa tra un risultato e l'altro

        await asyncio.sleep(3)  # Pausa tra una keyword e l'altra

# ✅ FUNZIONE PRINCIPALE
async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    connector = aiohttp.TCPConnector(limit=10, ssl=ssl_context)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        matches = get_matches_from_diretta_with_selenium()
        logging.info(f"Partite trovate su diretta.it: {len(matches)}")

        tasks = []
        for match in matches:
            task = process_match(session, match, bot)
            tasks.append(task)
            await asyncio.sleep(0.5)

        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
