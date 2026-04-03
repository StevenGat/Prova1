# Farmaci Prezzi — Web App su Render (gratis)

## Struttura
```
farmaci_render/
├── server.py            ← Flask backend + serve HTML
├── templates/
│   └── index.html       ← Webapp mobile-first
├── requirements.txt
├── render.yaml
└── .gitignore
```

## Deploy su Render (10 minuti, gratis)

### 1. Crea account GitHub
- Vai su github.com → Sign up (gratis)

### 2. Crea repository
- New repository → nome: `farmaci-prezzi` → Create
- Carica tutti i file di questa cartella

### 3. Crea account Render
- Vai su render.com → Sign up with GitHub

### 4. Nuovo servizio Web
- New → Web Service → collega il repo GitHub
- Render legge render.yaml automaticamente
- Clicca Deploy → attendi 2-3 minuti

### 5. Usa l'app
- Render ti dà un URL tipo: https://farmaci-prezzi.onrender.com
- Aprilo da iPhone Safari o PC Chrome
- Funziona ovunque, senza installare nulla!

## Nota: sleep dopo 15 minuti inattività
La prima apertura dopo inattività impiega ~30 secondi.
Per tenerlo sveglio: registrati su uptimerobot.com (gratis)
e aggiungi un monitor HTTP ogni 10 minuti sull'URL.
