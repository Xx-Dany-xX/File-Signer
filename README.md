# 📝 Code File Signer

**Code File Signer Pro** è un'app desktop Python che consente di:

* ✏️ Firmare digitalmente file di codice con SHA256 + UUID unici
* ✓ Verificare l'integrità dei file firmati
* 🗑️ Rimuovere firme digitali dai file

Supporta oltre 25 linguaggi di programmazione, tra cui Python, JavaScript, Java, C++, C#, HTML, CSS e molti altri.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📦 Requisiti

* Python 3.8+
* tkinter (incluso nella stdlib)

## ⚡ Installazione

1. Clona la repository:

```bash
git clone https://github.com/TUOUSER/file-signer-pro.git
cd file-signer-pro
```

2. (Opzionale) Crea e attiva un virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
venv\Scripts\activate     # Windows
```

3. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

## 🚀 Uso

Esegui l'app:

```bash
python src/filesigner.py
```

La GUI permette di:

* Selezionare file da firmare/verificare/rimuovere
* Firmare file con hash SHA256 univoco
* Verificare integrità del file
* Rimuovere firme in modo sicuro
* Visualizzare informazioni sulla licenza e watermark unico

<img width="1277" height="1308" alt="image" src="https://github.com/user-attachments/assets/52eee76e-e558-4dc7-a82d-c0bdf1e6e9d5" />

## 📌 Caratteristiche

* Firma digitale unica per macchina (UUID + SHA256)
* Supporto multilinguaggio (oltre 25 linguaggi)
* GUI moderna con progress bar e status realtime
* Rimozione firme senza alterare contenuto originale
* Watermark automatico e informazioni licenza

## 📝 Licenza

MIT License — vedi il file `LICENSE`.

## 💡 Note

* Non modificare manualmente un file dopo la firma per evitare hash non validi.
* La chiave di licenza è univoca per la macchina e non trasferibile.

## 🤝 Contribuire

Pull request e issue su GitHub sono benvenute.
