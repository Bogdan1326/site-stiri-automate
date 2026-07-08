import feedparser
import google.generativeai as genai
import os
import datetime
import re

cheie_api = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=cheie_api)
model = genai.GenerativeModel('gemini-1.5-flash')

feed_url = "https://www.theverge.com/rss/index.xml"
stiri = feedparser.parse(feed_url)

os.makedirs("content/posts", exist_ok=True)

for articol in stiri.entries[:3]:
    titlu = articol.title
    link = articol.link

    prompt = f"Scrie un articol scurt de 2 paragrafe in limba romana, cu un ton jurnalistic si captivant, bazat pe acest titlu: '{titlu}'. Nu adauga salutari sau alte introduceri, doar articolul direct."

    try:
        raspuns_ai = model.generate_content(prompt)
        continut = raspuns_ai.text

        nume_fisier = re.sub(r'\W+', '-', titlu.lower()) + ".md"
        cale_fisier = f"content/posts/{nume_fisier}"

        data_azi = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        continut_final = f"---\ntitle: \"{titlu.replace('\"', \"'\")}\"\ndate: {data_azi}\ndraft: false\n---\n\n{continut}\n\n[Citește sursa originală aici]({link})\n"
        
        with open(cale_fisier, "w", encoding="utf-8") as f:
            f.write(continut_final)
        print(f"Articol salvat: {titlu}")

    except Exception as e:
        print(f"A aparut o eroare la articolul {titlu}: {e}")