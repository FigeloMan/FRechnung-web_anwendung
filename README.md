# FRechnung Cloud Deployment (Render.com)

## Datenschutz-Architektur

Der Server ist vollstaendig stateless - er speichert keine Nutzerdaten.

- Firmendaten leben ausschliesslich im Browser (sessionStorage)
- Beim Schliessen des Tabs sind alle Daten geloescht
- Logos als Base64 im Request, nie am Server gespeichert
- Jeder PDF-Request ist self-contained

---

## Deployment auf Render.com

### Schritt 1 - Repo-Struktur (Cloud-Branch)

```
server.py              <- Flask App (cloud Version)
config_manager.py      <- Stateless Version (kein Keyring)
pdf_generator.py       <- unveraendert
requirements.txt
render.yaml
Procfile
frontend/
  index.html           <- Cloud Frontend (sessionStorage)
  favicon.ico
dejavu_fonts/          <- Schriftarten (optional)
```

### Schritt 2 - Render Account

1. render.com -> Sign up (kostenlos, keine Kreditkarte)
2. Mit GitHub verbinden

### Schritt 3 - Web Service erstellen

1. Dashboard -> New + -> Web Service
2. GitHub-Repo auswaehlen -> Connect
3. Einstellungen:
   - Name: frechnung
   - Region: Frankfurt (EU) -- wichtig fuer DSGVO
   - Branch: dein Cloud-Branch (z.B. web_application)
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn server:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
   - Plan: Free
4. -> Create Web Service

URL wird: https://frechnung.onrender.com

### Schritt 4 - Custom Domain (optional)

Settings -> Custom Domains -> Domain eintragen.
SSL wird automatisch ausgestellt (Let's Encrypt).

---

## Kostenloser Tier - Einschraenkungen

| Was          | Limit                                      |
|--------------|--------------------------------------------|
| RAM          | 512 MB                                     |
| Spin-down    | Nach 15 Min. Inaktivitaet schlaeft der Server |
| Aufwachzeit  | ca. 30 Sekunden beim ersten Request        |
| Bandwidth    | 100 GB/Monat                               |

Fuer produktiven Dauerbetrieb: Paid Plan ($7/Monat) = always-on.

---

## Lokaler Test

```bash
pip install -r requirements.txt
gunicorn server:app --bind 127.0.0.1:8080 --workers 2
```

Dann: http://localhost:8080

---

## Cloud- vs. Desktop-Branch Unterschiede

| Datei             | Desktop                    | Cloud                  |
|-------------------|----------------------------|------------------------|
| main.py           | pywebview App              | nicht vorhanden        |
| server.py         | lokaler Flask-Server       | Cloud Flask-Server     |
| config_manager.py | Keyring + Verschluesselung | Stateless (No-op)      |
| frontend/index.html | pywebview UI             | sessionStorage UI      |
| render.yaml       | nein                       | ja                     |
| requirements.txt  | mit keyring, cryptography  | ohne keyring           |
