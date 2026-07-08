import feedparser
from google import genai
import os
import re
import time
import logging
import datetime
from unidecode import unidecode

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# --- Configurare ---
# Poti adauga sau scoate surse RSS din lista asta
FEED_URLS = [
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/",
    "https://www.engadget.com/rss.xml",
]
ARTICOLE_PER_FEED = 2  # cate articole noi luam din fiecare sursa, la fiecare rulare
DIRECTOR_POSTS = "content/posts"
MODEL_AI = "gemini-2.5-flash"
PAUZA_INTRE_APELURI = 2  # secunde, ca sa nu lovim limita de rate a API-ului

cheie_api = os.environ.get("GEMINI_API_KEY")
if not cheie_api:
    raise SystemExit("Eroare: variabila de mediu GEMINI_API_KEY lipseste.")

client = genai.Client(api_key=cheie_api)

os.makedirs(DIRECTOR_POSTS, exist_ok=True)


def genereaza_slug(titlu: str) -> str:
    """Transforma titlul intr-un slug curat, fara diacritice, sigur pentru URL."""
    text = unidecode(titlu).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:80] or "articol"


def extrage_imagine(articol) -> str | None:
    """Incearca sa gaseasca o imagine reprezentativa in intrarea RSS."""
    if getattr(articol, "media_content", None):
        url = articol.media_content[0].get("url")
        if url:
            return url
    if getattr(articol, "media_thumbnail", None):
        url = articol.media_thumbnail[0].get("url")
        if url:
            return url
    for link in articol.get("links", []):
        if link.get("rel") == "enclosure" and "image" in link.get("type", ""):
            return link.get("href")
    return None


def genereaza_articol(titlu: str) -> str:
    prompt = (
        f"Scrie un articol scurt de 2 paragrafe in limba romana, cu un ton jurnalistic "
        f"si captivant, bazat pe acest titlu: '{titlu}'. "
        f"Nu adauga salutari sau alte introduceri, doar articolul direct."
    )
    raspuns = client.models.generate_content(model=MODEL_AI, contents=prompt)
    return (raspuns.text or "").strip()


def scrie_articol(titlu: str, link: str, continut: str, imagine: str | None, cale_fisier: str):
    data_azi = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    titlu_curat = titlu.replace('"', "'")

    linii = ["---", f'title: "{titlu_curat}"', f"date: {data_azi}", "draft: false"]
    if imagine:
        linii.append("cover:")
        linii.append(f'  image: "{imagine}"')
        linii.append(f'  alt: "{titlu_curat}"')
        linii.append("  relative: false")
    linii.append("---")

    continut_final = "\n".join(linii) + f"\n\n{continut}\n\n[Citește sursa originală aici]({link})\n"

    with open(cale_fisier, "w", encoding="utf-8") as f:
        f.write(continut_final)


def proceseaza_feed(feed_url: str, limita: int):
    log.info(f"Citire flux: {feed_url}")
    stiri = feedparser.parse(feed_url)

    if stiri.bozo:
        log.warning(f"Flux posibil corupt, sarim peste: {feed_url} ({stiri.bozo_exception})")
        return

    procesate = 0
    for articol in stiri.entries:
        if procesate >= limita:
            break

        titlu = articol.get("title", "").strip()
        link = articol.get("link", "")
        if not titlu or not link:
            continue

        slug = genereaza_slug(titlu)
        cale_fisier = os.path.join(DIRECTOR_POSTS, f"{slug}.md")

        if os.path.exists(cale_fisier):
            continue  # articol deja publicat, il sarim ca sa nu cheltuim API degeaba

        try:
            continut = genereaza_articol(titlu)
        except Exception as e:
            log.error(f"Eroare la generarea articolului '{titlu}': {e}")
            continue

        if not continut:
            log.warning(f"Raspuns AI gol pentru '{titlu}', sarim peste.")
            continue

        imagine = extrage_imagine(articol)
        scrie_articol(titlu, link, continut, imagine, cale_fisier)

        log.info(f"Articol salvat: {titlu}")
        procesate += 1
        time.sleep(PAUZA_INTRE_APELURI)

    log.info(f"Gata cu {feed_url}: {procesate} articole noi.")


def main():
    total_start = datetime.datetime.now()
    for feed_url in FEED_URLS:
        proceseaza_feed(feed_url, ARTICOLE_PER_FEED)
    durata = (datetime.datetime.now() - total_start).total_seconds()
    log.info(f"Rulare completa in {durata:.1f}s.")


if __name__ == "__main__":
    main()
