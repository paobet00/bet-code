import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# --- CONFIG ---
TELEGRAM_TOKEN = "8117577193:AAHnfVWVsgQ1a_8dqeJ5eMnQs1LQ9RAUrTA"
CHAT_ID = "69684347"

KEYWORDS = [
    "injury", "injuries", "out", "suspended", "resigns", "coach resigns",
    "financial", "bankrupt", "bajas", "lesión", "sanción",
    "blessés", "dimissioni", "problemi economici",
    "trainerwechsel", "verletzt", "finanzielle probleme"
]

RSS_FEEDS = [
    # Germania – 3. Liga
    "https://www.kicker.de/3-liga/news/rss",
    "https://www.reviersport.de/rss/3-liga.xml",
    "https://www.volksstimme.de/sport/rss",

    # Inghilterra – League Two / National League
    "https://feeds.bbci.co.uk/sport/football/league-two/rss.xml",
    "https://www.thenonleaguefootballpaper.com/feed/",
    "https://www.yorkshirepost.co.uk/sport/football/rss",

    # Spagna – Primera RFEF / Segunda B
    "https://www.mundodeportivo.com/rss/futbol/segunda-division",
    "https://e00-marca.uecdn.es/rss/futbol/segunda-division.xml",
    "https://www.estadiodeportivo.com/rss/rss-10.xml",

    # Africa RSS
    "https://www.kickoff.com/rss",
    "https://www.soccerladuma.co.za/feed",
    "https://www.completesports.com/category/football/feed/",
    "https://www.kingfut.com/feed/",
    "https://www.lebuteur.com/rss"
]

# --- FUNZIONI ---
def check_keywords(text):
    """Controlla se il testo contiene almeno una keyword"""
    return any(kw.lower() in text.lower() for kw in KEYWORDS)

def fetch_rss():
    """Raccoglie notizie dai feed RSS filtrando per keyword"""
    results = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                text = entry.title + " " + entry.get("summary", "")
                if check_keywords(text):
                    results.append((entry.title, entry.link))
        except Exception as e:
            print(f"Errore RSS {url}: {e}")
    return results

def fetch_site(url, css_selector, session=None):
    """Scraping siti web senza RSS filtrando per keyword"""
    results = []
    session = session or requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36"
    }
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select(css_selector):
            title = item.get_text(strip=True)
            link = item.get("href")
            if link and check_keywords(title):
                if link.startswith("/"):
                    link = url.rstrip("/") + link
                results.append((title, link))
    except Exception as e:
        print(f"Errore scraping {url}: {e}")
    return results

def notify(news):
    """Invia le notizie filtrate via Telegram"""
    bot = Bot(TELEGRAM_TOKEN)
    for title, link in news:
        bot.send_message(chat_id=CHAT_ID, text=f"📌 {title}\n🔗 {link}")

# --- MAIN ---
def main():
    news = []
    session = requests.Session()

    # 1. RSS feeds
    news.extend(fetch_rss())

    # 2. Siti africani / senza RSS
    sites = [
        ("https://www.kickoff.com/sa-news", "article h2 a"),
        ("https://www.soccerladuma.co.za/local", "article h2 a"),
        ("https://www.completesports.com/category/football/", "h2.entry-title a"),
        ("https://www.kingfut.com/category/football/", "h3.entry-title a"),
        ("https://www.lebuteur.com/", "h2.entry-title a"),
        ("https://www.lapresse.tn/category/sport/football/", "h2 a"),
        ("https://lematin.ma/football/", "div.article a")
    ]

    for url, selector in sites:
        news.extend(fetch_site(url, selector, session=session))

    # Rimuove duplicati
    news = list(dict.fromkeys(news))

    # Invia su Telegram
    if news:
        notify(news)
        print(f"Inviate {len(news)} notizie al bot.")
    else:
        print("Nessuna notizia rilevante trovata.")

if __name__ == "__main__":
    main()
