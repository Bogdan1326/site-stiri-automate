import feedparser
from google import genai
import os
import datetime
import re

# 1. Ne conectam folosind noua librarie standard
cheie_api = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=cheie_api)

# 2. Citim stirile (am pastrat The Verge ca exemplu)
feed_url = "https://www.theverge.com/rss/index.xml"
stiri = feedparser.parse(feed_url)

os.makedirs("content/posts", exist_ok=True)

# 3. Generam continutul
for articol in stiri.entries[:3]:
    titlu = articol.title
    link = articol.link

    prompt = f"Scrie un articol scurt de 2 paragrafe in limba romana, cu un ton jurnalistic si captivant, bazat pe acest titlu: '{titlu}'. Nu adauga salutari sau alte introduceri, doar articolul direct."

    try:
        # Folosim noul model si format de apelare
        raspuns_ai = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        continut = raspuns_ai.text

        nume_fisier = re.sub(r'\W+', '-', titlu.lower()) + ".md"
        cale_fisier = f"content/posts/{nume_fisier}"

        data_azi = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        titlu_curat = titlu.replace('"', "'")
        
        continut_final = f"""---
title: "{titlu_curat}"
date: {data_azi}
draft: false
---

{continut}

[Citește sursa originală aici]({link})
"""
        with open(cale_fisier, "w", encoding="utf-8") as f:
            f.write(continut_final)
        print(f"Articol salvat cu succes: {titlu}")

    except Exception as e:
        print(f"Eroare la articolul '{titlu}': {e}")