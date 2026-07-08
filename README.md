# site-stiri-automate

Site de știri tech generat automat, în limba română, folosind AI (Gemini) și publicat zilnic pe GitHub Pages cu Hugo + tema PaperMod.

## Cum funcționează

În fiecare noapte (03:00 UTC), workflow-ul din `.github/workflows/automatizare.yml`:

1. Citește mai multe fluxuri RSS (`FEED_URLS` din `scraper.py`).
2. Pentru fiecare articol nou (care nu a mai fost publicat), generează un text în română cu Gemini.
3. Salvează articolele ca fișiere Markdown în `content/posts/` **și le comite înapoi în repo**, astfel încât site-ul acumulează un istoric real de articole, nu doar cele din ultima rulare.
4. Construiește site-ul cu Hugo și îl publică pe branch-ul `gh-pages`.

## Setup local (opțional, pentru testare)

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="cheia-ta"
python scraper.py

git clone https://github.com/adityatelange/hugo-PaperMod themes/PaperMod --depth=1
hugo server
```

## Configurare

- **Surse RSS**: editează lista `FEED_URLS` din `scraper.py`.
- **Câte articole per sursă**: `ARTICOLE_PER_FEED` din `scraper.py`.
- **Aspectul site-ului**: `hugo.toml` (params PaperMod) și `assets/css/extended/custom.css` pentru stiluri proprii.
- **Secretul `GEMINI_API_KEY`**: se setează în Settings → Secrets and variables → Actions, în repo-ul de pe GitHub.

## Necesar în repo (dacă lipsesc)

Pentru ca temă PaperMod să afișeze corect favicon-ul, adaugă în `static/`:
`favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`.
