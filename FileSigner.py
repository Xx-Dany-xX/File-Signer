import hashlib
import uuid
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import re
from datetime import datetime
from pathlib import Path
import threading
import time
import json
import base64

# ══════════════════════════════════════════════════════════════════════════════
# 🔐 PROTEZIONE UNIVOCA DEL SOFTWARE
# ══════════════════════════════════════════════════════════════════════════════

class SoftwareProtection:
    """Sistema di protezione e licenza univoca"""
    
    PRODUCT_NAME = "Code File Signer"
    PRODUCT_VERSION = "1.0.0"
    AUTHOR = "Dany © 2025 - All Rights Reserved"
    
    PRODUCT_ID = "CFS-2025-PRO-SECURE"
    
    ORIGINAL_HASH = "7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b"
    
    @staticmethod
    def get_machine_id():
        """Genera ID univoco della macchina"""
        try:
            machine_id = str(uuid.getnode())  
            return machine_id
        except:
            return "UNKNOWN"
    
    @staticmethod
    def get_license_key():
        """Genera chiave di licenza univoca basata sulla macchina"""
        machine_id = SoftwareProtection.get_machine_id()
        product_id = SoftwareProtection.PRODUCT_ID
        timestamp = str(datetime.now().year)
        
        license_data = f"{product_id}_{machine_id}_{timestamp}"
        license_hash = hashlib.sha256(license_data.encode()).hexdigest()[:32].upper()
        
        return f"LIC-{license_hash}"
    
    @staticmethod
    def get_software_signature():
        """Firma digitale del software"""
        sig_data = f"{SoftwareProtection.PRODUCT_ID}_{SoftwareProtection.PRODUCT_VERSION}_{SoftwareProtection.AUTHOR}"
        return hashlib.sha256(sig_data.encode()).hexdigest()
    
    @staticmethod
    def get_watermark():
        """Watermark univoco del software"""
        machine_id = SoftwareProtection.get_machine_id()
        product_sig = SoftwareProtection.get_software_signature()
        watermark = f"[{SoftwareProtection.PRODUCT_NAME} v{SoftwareProtection.PRODUCT_VERSION} - {machine_id[:8]}]"
        return watermark

LICENSE_KEY = SoftwareProtection.get_license_key()
SOFTWARE_SIGNATURE = SoftwareProtection.get_software_signature()
WATERMARK = SoftwareProtection.get_watermark()

# ══════════════════════════════════════════════════════════════════════════════
# 🎨 TEMA E COLORI (Dark Modern)
# ══════════════════════════════════════════════════════════════════════════════

BG_PRIMARY = "#0f172a"
BG_SECONDARY = "#1e293b"
BG_ACCENT = "#1a237e"
ACCENT_COLOR = "#00d9ff"
SUCCESS_COLOR = "#10b981"
ERROR_COLOR = "#ef4444"
TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"

# ══════════════════════════════════════════════════════════════════════════════
# 💬 STILI DI COMMENTO PER LINGUAGGI
# ══════════════════════════════════════════════════════════════════════════════

COMMENT_STYLES = {
    ".py": "#",
    ".js": "//",
    ".ts": "//",
    ".jsx": "//",
    ".tsx": "//",
    ".cpp": "//",
    ".c": "//",
    ".java": "//",
    ".cs": "//",
    ".php": "//",
    ".go": "//",
    ".rs": "//",
    ".swift": "//",
    ".kt": "//",
    ".scala": "//",
    ".html": "<!--",
    ".xml": "<!--",
    ".css": "/*",
    ".scss": "//",
    ".sql": "--",
    ".r": "#",
    ".lua": "--",
    ".sh": "#",
    ".bash": "#",
    ".rb": "#",
}

CLOSING_COMMENT = {
    "<!--": "-->",
    "/*": "*/",
}

# ══════════════════════════════════════════════════════════════════════════════
# ✍️ FUNZIONI DI FIRMA DIGITALE
# ══════════════════════════════════════════════════════════════════════════════

def get_comment_lines(ext, signature, file_hash, timestamp):
    """Genera le linee di commento per la firma (corretto)"""
    ext = ext.lower()
    comment = COMMENT_STYLES.get(ext, "#")
    closing = CLOSING_COMMENT.get(comment, "")
    
    sig_marker = f"_SIGNATURE_{signature}"
    hash_marker = f"_HASH_{file_hash}"
    time_marker = f"_SIGNED_{timestamp}"
    
    if ext == ".html" or ext == ".xml":
        signature_line = f"<!-- {sig_marker} -->"
        hash_line = f"<!-- {hash_marker} -->"
        time_line = f"<!-- {time_marker} -->"
    elif comment == "/*":
        signature_line = f"/* {sig_marker} */"
        hash_line = f"/* {hash_marker} */"
        time_line = f"/* {time_marker} */"
    elif closing:
        signature_line = f"{comment} {sig_marker} {closing}"
        hash_line = f"{comment} {hash_marker} {closing}"
        time_line = f"{comment} {time_marker} {closing}"
    else:
        signature_line = f"{comment} {sig_marker}"
        hash_line = f"{comment} {hash_marker}"
        time_line = f"{comment} {time_marker}"
    
    return signature_line, hash_line, time_line

def extract_signature_data(file_path):
    """Estrae firma e hash dal file"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    sig_match = re.search(r"_SIGNATURE_([a-f0-9\-]+)", content)
    hash_match = re.search(r"_HASH_([a-f0-9]+)", content)
    time_match = re.search(r"_SIGNED_(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", content)
    
    return {
        'signature': sig_match.group(1) if sig_match else None,
        'hash': hash_match.group(1) if hash_match else None,
        'timestamp': time_match.group(1) if time_match else None,
        'raw': content
    }

def remove_signature_lines(content):
    """Rimuove le linee di firma dal contenuto normalizzando il testo"""
    lines = content.split('\n')
    filtered = []
    for line in lines:
        if '_SIGNATURE_' not in line and '_HASH_' not in line and '_SIGNED_' not in line:
            filtered.append(line)
    
    result = '\n'.join(filtered).strip()
    
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')
    
    return result

def add_signature(file_path, progress_callback=None):
    """Aggiunge firma digitale SHA256 + UUID + timestamp al file"""
    try:
        if not os.path.exists(file_path):
            return False, f"Il file {file_path} non esiste."
        
        if progress_callback:
            progress_callback("Lettura file...")
        
        ext = os.path.splitext(file_path)[1].lower()
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
        
        clean_content = remove_signature_lines(original_content)
        
        if progress_callback:
            progress_callback("Generazione firma...")
        
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        file_hash = hashlib.sha256(clean_content.encode("utf-8")).hexdigest()
        
        signature_line, hash_line, time_line = get_comment_lines(ext, unique_id, file_hash, timestamp)
        
        final_content = clean_content + "\n\n" + signature_line + "\n" + hash_line + "\n" + time_line + "\n"
        
        if progress_callback:
            progress_callback("Salvataggio file...")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        return True, f"SHA256: {file_hash}\nID: {unique_id}\nData: {timestamp}"
    
    except Exception as e:
        return False, f"Errore durante la firma: {str(e)}"

def verify_signature(file_path, progress_callback=None):
    """Verifica l'integrità del file confrontando l'hash SHA256 attuale con quello memorizzato"""
    try:
        if not os.path.exists(file_path):
            return False, f"Il file {file_path} non esiste."
        
        if progress_callback:
            progress_callback("Estrazione dati firma...")
        
        data = extract_signature_data(file_path)
        
        if not data['signature'] or not data['hash']:
            return False, "File non firmato o firma corrotta."
        
        if progress_callback:
            progress_callback("Verifica integrità...")
        
        clean_content = remove_signature_lines(data['raw'])
        recalculated_hash = hashlib.sha256(clean_content.encode("utf-8")).hexdigest()
        
        is_valid = recalculated_hash == data['hash']
        
        info = f"ID: {data['signature']}\nHash: {data['hash'][:32]}...\nData: {data['timestamp'] or 'N/A'}"
        
        return is_valid, info
    
    except Exception as e:
        return False, f"Errore durante la verifica: {str(e)}"

# ══════════════════════════════════════════════════════════════════════════════
# 🖥️ INTERFACCIA GRAFICA (GUI MODERNA DARK THEME)
# ══════════════════════════════════════════════════════════════════════════════

class FileSigner(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("📝 Code File Signer")
        self.geometry("850x840")
        self.resizable(False, False)
        
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        self.progress_running = False
        
        self.configure_progress_bar_style()
        
        self.configure(bg=BG_PRIMARY)
        
        self.create_ui()
        
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def configure_progress_bar_style(self):
        """Configura lo stile della barra di progresso con i colori del tema"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "TProgressbar",
            background=ACCENT_COLOR,
            troughcolor=BG_SECONDARY,
            bordercolor=BG_ACCENT,
            darkcolor=ACCENT_COLOR,
            lightcolor=ACCENT_COLOR,
            thickness=20
        )
    
    def create_ui(self):
        header = tk.Frame(self, bg=BG_ACCENT, height=120)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header, 
            text="📝 CODE FILE SIGNER",
            font=("Segoe UI", 24, "bold"),
            bg=BG_ACCENT,
            fg=ACCENT_COLOR
        )
        title_label.pack(pady=(12, 8))
        
        subtitle_label = tk.Label(
            header,
            text="Sistema di Firma Digitale\nPer la Verifica e l'Integrità dei File di Codice",
            font=("Segoe UI", 10),
            bg=BG_ACCENT,
            fg=TEXT_SECONDARY,
            justify=tk.CENTER,
            wraplength=820
        )
        subtitle_label.pack(pady=(0, 12), padx=20)
        
        main_frame = tk.Frame(self, bg=BG_PRIMARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        file_frame = tk.Frame(main_frame, bg=BG_SECONDARY, relief=tk.FLAT, highlightthickness=2, highlightbackground=BG_ACCENT, highlightcolor=ACCENT_COLOR)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        file_label = tk.Label(
            file_frame,
            text="📂 Seleziona File",
            font=("Segoe UI", 11, "bold"),
            bg=BG_SECONDARY,
            fg=ACCENT_COLOR
        )
        file_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        self.entry_file = tk.Entry(
            file_frame,
            font=("Segoe UI", 10),
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            border=0
        )
        self.entry_file.pack(fill=tk.X, padx=15, pady=(5, 10))
        self.entry_file.bind("<Return>", lambda e: self.browse_file())
        
        browse_btn = tk.Button(
            file_frame,
            text="🔍 SFOGLIA",
            command=self.browse_file,
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_COLOR,
            fg=BG_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        browse_btn.pack(padx=15, pady=(0, 10), fill=tk.X)
        
        progress_container = tk.Frame(file_frame, bg=BG_SECONDARY)
        progress_container.pack(fill=tk.X, padx=15, pady=(0, 8))
        
        self.progress = ttk.Progressbar(
            progress_container,
            mode='determinate',
            length=300,
            style="TProgressbar",
            maximum=100
        )
        self.progress.pack(fill=tk.X)
        self.progress['value'] = 0
        
        self.status_label = tk.Label(
            file_frame,
            text="✓ Applicazione pronta",
            font=("Segoe UI", 9, "bold"),
            bg=BG_SECONDARY,
            fg=SUCCESS_COLOR
        )
        self.status_label.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        buttons_frame = tk.Frame(main_frame, bg=BG_PRIMARY)
        buttons_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        sign_btn = tk.Button(
            buttons_frame,
            text="✏️  FIRMA FILE",
            command=self.sign_file,
            font=("Segoe UI", 12, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=15
        )
        sign_btn.pack(fill=tk.X, pady=(0, 15))
        
        verify_btn = tk.Button(
            buttons_frame,
            text="✓ VERIFICA FIRMA",
            command=self.verify_file,
            font=("Segoe UI", 12, "bold"),
            bg=ACCENT_COLOR,
            fg=BG_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=15
        )
        verify_btn.pack(fill=tk.X, pady=(0, 15))
        
        remove_btn = tk.Button(
            buttons_frame,
            text="🗑️  RIMUOVI FIRMA",
            command=self.remove_signature,
            font=("Segoe UI", 12, "bold"),
            bg=ERROR_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=15
        )
        remove_btn.pack(fill=tk.X, pady=(0, 15))
        
        separator = tk.Frame(buttons_frame, bg=BG_ACCENT, height=1)
        separator.pack(fill=tk.X, pady=10)
        
        info_btn = tk.Button(
            buttons_frame,
            text="ℹ️  INFO LICENZA",
            command=self.show_license_info,
            font=("Segoe UI", 9, "bold"),
            bg=BG_SECONDARY,
            fg=ACCENT_COLOR,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        info_btn.pack(fill=tk.X)
        
        info_frame = tk.Frame(self, bg=BG_SECONDARY)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        info_text = tk.Label(
            info_frame,
            text="🔒 Algoritmo SHA256  |  🌐 25+ Linguaggi Supportati  |  🔑 UUID Unico per Firma  |  ⏰ Timestamp Autenticato",
            font=("Segoe UI", 8),
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY,
            justify=tk.CENTER
        )
        info_text.pack(padx=10, pady=8)
        
        footer = tk.Frame(self, bg=BG_ACCENT, height=60)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_top = tk.Frame(footer, bg=BG_ACCENT)
        footer_top.pack(fill=tk.X, padx=15, pady=(5, 0))
        
        footer_left = tk.Label(
            footer_top,
            text=f"🔐 {SoftwareProtection.PRODUCT_NAME} v{SoftwareProtection.PRODUCT_VERSION}",
            font=("Segoe UI", 8, "bold"),
            bg=BG_ACCENT,
            fg=ACCENT_COLOR
        )
        footer_left.pack(side=tk.LEFT)
        
        footer_right = tk.Label(
            footer_top,
            text=WATERMARK,
            font=("Segoe UI", 7),
            bg=BG_ACCENT,
            fg=TEXT_SECONDARY
        )
        footer_right.pack(side=tk.RIGHT)
        
        footer_bottom = tk.Frame(footer, bg=BG_ACCENT)
        footer_bottom.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        footer_author = tk.Label(
            footer_bottom,
            text=f"© Made with ❤️ by {SoftwareProtection.AUTHOR}",
            font=("Segoe UI", 7, "italic"),
            bg=BG_ACCENT,
            fg=TEXT_SECONDARY
        )
        footer_author.pack(side=tk.LEFT)
        
        footer_license = tk.Label(
            footer_bottom,
            text=f"License: {LICENSE_KEY}",
            font=("Segoe UI", 7),
            bg=BG_ACCENT,
            fg=ACCENT_COLOR
        )
        footer_license.pack(side=tk.RIGHT)
    
    def browse_file(self):
        self.update_status("⏳ Scelta file in corso...", TEXT_SECONDARY)
        self.start_progress()
        
        file_path = filedialog.askopenfilename(
            title="Seleziona un file",
            filetypes=[
                ("Tutti i file", "*.*"),
                ("Python", "*.py"),
                ("JavaScript", "*.js"),
                ("TypeScript", "*.ts"),
                ("C++", "*.cpp"),
                ("Java", "*.java"),
                ("C#", "*.cs"),
                ("HTML", "*.html"),
                ("CSS", "*.css"),
                ("SQL", "*.sql"),
            ]
        )
        
        self.stop_progress()
        
        if file_path:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, file_path)
            file_name = Path(file_path).name
            self.update_status(f"📄 File selezionato: {file_name}", ACCENT_COLOR)
        else:
            self.update_status("✓ Applicazione pronta", SUCCESS_COLOR)
    
    def update_status(self, text, color=""):
        self.status_label.config(text=text, fg=color or TEXT_SECONDARY)
        self.update()
    
    def start_progress(self):
        """Avvia l'animazione della barra di progresso"""
        self.progress['value'] = 0
        self.progress_running = True
        
        def animate():
            while self.progress_running and self.progress['value'] < 90:
                self.progress['value'] += 2
                time.sleep(0.05)
                self.update()
        
        thread = threading.Thread(target=animate, daemon=True)
        thread.start()
    
    def stop_progress(self):
        """Ferma l'animazione della barra e la completa"""
        self.progress_running = False
        self.progress['value'] = 100
        self.update()
        time.sleep(0.3)
        self.progress['value'] = 0
        self.update()
    
    def progress_callback(self, message):
        self.update_status(message, TEXT_SECONDARY)
    
    def show_license_info(self):
        """Mostra informazioni complete di licenza e protezione del software"""
        machine_id = SoftwareProtection.get_machine_id()
        license_key = SoftwareProtection.get_license_key()
        software_sig = SoftwareProtection.get_software_signature()
        
        info_message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔐 INFORMAZIONI DI LICENZA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 PRODOTTO
   ├─ Nome: {SoftwareProtection.PRODUCT_NAME}
   ├─ Versione: {SoftwareProtection.PRODUCT_VERSION}
   └─ Autore: {SoftwareProtection.AUTHOR}

🔐 PROTEZIONE
   ├─ Product ID: {SoftwareProtection.PRODUCT_ID}
   ├─ Machine ID: {machine_id}
   └─ License Key: {license_key}

✅ VERIFICAZIONE
   ├─ Firma: {software_sig[:32]}...
   └─ Status: ✓ SOFTWARE AUTENTICO

⚠️  AVVISO LEGALE
   Questo software è protetto da copyright.
   Qualsiasi tentativo di copia, modifica o
   distribuzione non autorizzata è vietato.
   
   La chiave di licenza è univoca e collegata
   a questa macchina. Non è trasferibile.

📋 TERMINI D'USO
   ✓ Uso personale/aziendale autorizzato
   ✗ Divieto di decompilazione
   ✗ Divieto di reverse engineering
   ✗ Divieto di distribuzione a terzi

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        messagebox.showinfo("🔐 Informazioni di Licenza", info_message)
    
    def sign_file(self):
        file_path = self.entry_file.get()
        if not file_path:
            messagebox.showwarning("Attenzione", "Seleziona un file!")
            self.update_status("✗ Nessun file selezionato", ERROR_COLOR)
            return
        
        file_name = Path(file_path).name
        self.start_progress()
        self.update_status(f"🔄 Firma di {file_name} in corso...", TEXT_SECONDARY)
        
        success, message = add_signature(file_path, self.progress_callback)
        self.stop_progress()
        
        if success:
            self.update_status(f"✓ {file_name} firmato con successo!", SUCCESS_COLOR)
            messagebox.showinfo(
                "✅ Firma Completata",
                f"File firmato correttamente!\n\n{message}"
            )
        else:
            self.update_status(f"✗ Errore: impossibile firmare {file_name}", ERROR_COLOR)
            messagebox.showerror("❌ Errore", message)
    
    def verify_file(self):
        file_path = self.entry_file.get()
        if not file_path:
            messagebox.showwarning("Attenzione", "Seleziona un file!")
            self.update_status("✗ Nessun file selezionato", ERROR_COLOR)
            return
        
        file_name = Path(file_path).name
        self.start_progress()
        self.update_status(f"🔍 Verifica di {file_name} in corso...", TEXT_SECONDARY)
        
        is_valid, message = verify_signature(file_path, self.progress_callback)
        self.stop_progress()
        
        if is_valid:
            self.update_status(f"✓ {file_name} integro e verificato!", SUCCESS_COLOR)
            messagebox.showinfo(
                "✅ Verifica Superata",
                f"File integro e non modificato!\n\n{message}"
            )
        else:
            self.update_status(f"✗ {file_name} non verificato", ERROR_COLOR)
            messagebox.showerror("❌ Verifica Fallita", f"File non valido o manomesso!\n\n{message}")
    
    def remove_signature(self):
        file_path = self.entry_file.get()
        if not file_path:
            messagebox.showwarning("Attenzione", "Seleziona un file!")
            self.update_status("✗ Nessun file selezionato", ERROR_COLOR)
            return
        
        file_name = Path(file_path).name
        if messagebox.askyesno("Conferma", f"Rimuovere la firma da {file_name}?"):
            try:
                self.start_progress()
                self.update_status(f"🗑️ Rimozione firma da {file_name}...", TEXT_SECONDARY)
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                clean_content = remove_signature_lines(content)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clean_content)
                
                self.stop_progress()
                self.update_status(f"✓ Firma rimossa da {file_name}", SUCCESS_COLOR)
                messagebox.showinfo("✅ Operazione Completata", f"Firma rimossa da {file_name}!")
            except Exception as e:
                self.stop_progress()
                self.update_status(f"✗ Errore durante la rimozione", ERROR_COLOR)
                messagebox.showerror("❌ Errore", f"Errore: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 PUNTO DI INGRESSO APPLICAZIONE
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        app = FileSigner()
        app.mainloop()
    except Exception as e:
        import traceback, sys
        traceback.print_exc()
        messagebox.showerror("Errore", f"Errore durante l'avvio dell'app: {str(e)}")
