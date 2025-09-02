CryptoAuto — prosty skrypt do pobierania cen kryptowalut i akcji

Opis
- Pobiera ceny z Yahoo Finance (przez yfinance) i CoinGecko (opcjonalnie przez requests).
- Zapisuje dane do CSV, JSON lub SQLite.
- Harmonogram aktualizacji co 10 minut (konfigurowalne).
- Generuje prosty raport zmian procentowych i wypisuje na konsolę (opcjonalnie wysyła emailem).

Szybki start
1. Zainstaluj zależności:

```powershell
python -m pip install -r requirements.txt
```

2. Skonfiguruj `config.yaml` (domyślne symbole znajdują się już w pliku).
3. Uruchom:

Run once:
```powershell
python -m cryptoauto --once
```

Run as long-running scheduler:
```powershell
python -m cryptoauto
```

By default the application prints raw fetched rows and the generated report to the console each cycle. To disable console output use:

```powershell
python -m cryptoauto --no-console
```

Pliki
- `cryptoauto/` — kod źródłowy
- `config.yaml` — konfiguracja
- `requirements.txt` — wymagane pakiety

Uwagi
- Skrypt jest przykładam. Przed użyciem w produkcji sprawdź limity API i ustawienia bezpieczeństwa.

Docker
------
Build and run with Docker:

```powershell
docker build -t cryptoauto .
docker run --rm -it cryptoauto
```

Or using docker-compose:

```powershell
docker-compose up --build
```

Publish to GitHub
-----------------
1. Create a new repository on GitHub.
2. Initialize git locally and push:

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/blaszkaaa/CryptoAuto.git
git push -u origin main
```

CI is provided via `.github/workflows/ci.yml` which runs tests on push.
