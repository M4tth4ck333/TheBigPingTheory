# plugins/jan_eye_report_viewer.py

import tkinter as tk
from tkinter import ttk
from sqlalchemy.exc import SQLAlchemyError # Muss für die Fehlerbehandlung importiert werden

# --- Annahmen ---
# Da die Basisklasse nicht definiert ist, wird hier eine Minimal-Definition für den Testlauf angenommen
class GUIStreamPluginBase(object):
    def __init__(self):
        self.gui_frame = None
    def create_gui(self, parent):
        self.gui_frame = ttk.Frame(parent, padding="10 10 10 10")
        self.gui_frame.columnconfigure(0, weight=1)
        return self.gui_frame

# Importieren Sie den DBManager und Modelle
# ANMERKUNG: db_manager_updated.py MUSS die Klassen DBManager, CodeAnalysisReport, Module, FileHash enthalten.
from db_manager_updated import DBManager, CodeAnalysisReport, Module, FileHash 


class JanEyeReportViewer(GUIStreamPluginBase):
    name = "Jan's Eye Reports"
    type = "analysis"
    stream_type = "report"
    description = "Zeigt Code-Analyseberichte von Jan's Eye an."
    author = "m4tt~h4ck"
    version = "1.0"

    def __init__(self):
        super().__init__() # KORREKTUR: Falsche Syntax entfernt
        self.db_manager = DBManager() # Instanz des DBManager
        self.reports = [] # Liste zum Speichern der abgerufenen Berichte

    def create_gui(self, parent):
        """
        Erstellt die GUI-Elemente für das Jan's Eye Report Viewer Plugin.
        """
        frame = super().create_gui(parent) # Basis-Frame von GUIStreamPluginBase
        
        # --- Titel-Label ---
        self.title_label = tk.Label(frame, text="Jan's Eye Code-Analyseberichte:", 
                                    fg="#FFD700", bg="#222222", font=("Consolas", 14, "bold"))
        self.title_label.pack(pady=(10, 5), fill=tk.X)

        # --- Treeview Container und Scrollbar ---
        tree_frame = tk.Frame(frame)
        tree_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.report_tree = ttk.Treeview(tree_frame, 
                                        columns=("ID", "Module", "File", "Status", "Time", "Summary"), 
                                        show="headings", 
                                        height=10)
        
        # Scrollbar für die Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Spaltenüberschriften definieren
        self.report_tree.heading("ID", text="ID", anchor=tk.W)
        self.report_tree.heading("Module", text="Modul", anchor=tk.W)
        self.report_tree.heading("File", text="Datei", anchor=tk.W)
        self.report_tree.heading("Status", text="Status", anchor=tk.W)
        self.report_tree.heading("Time", text="Zeit", anchor=tk.W)
        self.report_tree.heading("Summary", text="Zusammenfassung", anchor=tk.W)

        # Spaltenbreiten anpassen
        self.report_tree.column("ID", width=40, stretch=tk.NO)
        self.report_tree.column("Module", width=120, stretch=tk.NO)
        self.report_tree.column("File", width=120, stretch=tk.NO)
        self.report_tree.column("Status", width=80, stretch=tk.NO)
        self.report_tree.column("Time", width=150, stretch=tk.NO)
        self.report_tree.column("Summary", width=300, stretch=tk.YES)

        # --- Detailansicht ---
        self.detail_label = tk.Label(frame, text="Detaillierte Findings:", 
                                     fg="#00FFFF", bg="#222222", font=("Consolas", 11))
        self.detail_label.pack(pady=(10, 2), fill=tk.X)
        
        self.detail_text = tk.Text(frame, bg="#181818", fg="#FFFFFF", height=8, width=80, 
                                   state="disabled", font=("Consolas", 10))
        self.detail_text.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)

        # Bindung für die Auswahl in der Treeview
        self.report_tree.bind("<<TreeviewSelect>>", self.on_report_select)

        # --- Refresh Button ---
        self.refresh_button = tk.Button(frame, text="Berichte aktualisieren", 
                                        command=self.update_gui, 
                                        bg="#0066CC", fg="white", font=("Consolas", 10, "bold"),
                                        relief=tk.RAISED, bd=2, padx=5, pady=2)
        self.refresh_button.pack(pady=5)

        return frame

    def update_gui(self, data=None):
        """
        Aktualisiert die Anzeige der Berichte in der GUI.
        """
        self.report_tree.delete(*self.report_tree.get_children()) # Vorherige Einträge löschen
        
        # Abrufen der Berichte und Vorladen der Daten
        self.reports = self.db_manager.get_code_analysis_reports(limit=50) 

        if not self.reports:
            self.report_tree.insert("", tk.END, values=("", "", "", "", "", "Keine Berichte gefunden."))
            return

        # Vordefinieren von Dictionaries für effizienteres Nachschlagen
        module_cache = {}
        file_cache = {}

        for report in self.reports:
            module_name = "N/A"
            file_name = "N/A"
            
            # --- Modulnamen abrufen (mit Caching) ---
            if report.module_id:
                if report.module_id not in module_cache:
                    session = self.db_manager.get_session() 
                    try:
                        module = session.query(Module).filter_by(id=report.module_id).first()
                        module_cache[report.module_id] = module.name if module else "N/A"
                    except SQLAlchemyError as e:
                        print(f"Fehler beim Abrufen des Moduls für Bericht {report.id}: {e}")
                        module_cache[report.module_id] = "N/A"
                    finally:
                        session.close()
                module_name = module_cache[report.module_id]
            
            # --- Dateinamen abrufen (mit Caching) ---
            if report.file_hash_id:
                if report.file_hash_id not in file_cache:
                    session = self.db_manager.get_session()
                    try:
                        file_hash_entry = session.query(FileHash).filter_by(id=report.file_hash_id).first()
                        file_cache[report.file_hash_id] = file_hash_entry.filename if file_hash_entry else "N/A"
                    except SQLAlchemyError as e:
                        print(f"Fehler beim Abrufen des FileHash für Bericht {report.id}: {e}")
                        file_cache[report.file_hash_id] = "N/A"
                    finally:
                        session.close()
                file_name = file_cache[report.file_hash_id]

            # Eintrag in die Treeview
            self.report_tree.insert("", tk.END, 
                                    values=(report.id, module_name, file_name, report.status, 
                                            report.analysis_time.strftime('%Y-%m-%d %H:%M:%S'), 
                                            report.summary))

        # Detailansicht leeren
        self.detail_text.config(state="normal")
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.config(state="disabled")

    def on_report_select(self, event):
        """
        Wird aufgerufen, wenn ein Bericht in der Treeview ausgewählt wird.
        Zeigt die detaillierten Findings an.
        """
        selected_item = self.report_tree.focus()
        if not selected_item:
            return

        item_values = self.report_tree.item(selected_item, 'values')
        if not item_values:
            return

        try:
            report_id = int(item_values[0]) # Die ID des ausgewählten Berichts
        except ValueError:
            return # Abbruch, wenn die ID keine gültige Zahl ist

        # Den vollständigen Bericht aus der Liste der abgerufenen Berichte finden
        selected_report = next((r for r in self.reports if r.id == report_id), None)

        self.detail_text.config(state="normal")
        self.detail_text.delete(1.0, tk.END)
        
        if selected_report and selected_report.findings:
            findings_str = ""
            # Annahme: findings ist eine Liste von Dictionaries
            for finding in selected_report.findings:
                # Sicherstellen, dass die Keys vorhanden sind
                findings_str += f"Type: {finding.get('type', 'N/A')}\n"
                findings_str += f"Location: {finding.get('location', 'N/A')}\n"
                findings_str += f"Detail: {finding.get('detail', 'N/A')}\n\n"
            
            self.detail_text.insert(tk.END, findings_str.strip())
        else:
            self.detail_text.insert(tk.END, "Keine detaillierten Findings verfügbar.")

        self.detail_text.config(state="disabled")

    def run(self, **kwargs):
        """
        Startet das Plugin und aktualisiert die GUI.
        """
        if self.gui_frame:
            self.update_gui()


# --- Beispiel für die Einbindung in die Hauptanwendung (für Testzwecke) ---
if __name__ == "__main__":
    
    # --- DUMMY DBManager und MODELLE (NUR FÜR DEN TESTLAUF) ---
    # Ersetzen Sie dies durch Ihre tatsächliche db_manager_updated.py
    
    class DummyModule:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    class DummyFileHash:
        def __init__(self, id, filename):
            self.id = id
            self.filename = filename

    class DummyReport:
        def __init__(self, id, module_id, file_hash_id, status, summary, findings):
            self.id = id
            self.module_id = module_id
            self.file_hash_id = file_hash_id
            self.status = status
            self.summary = summary
            self.findings = findings
            self.analysis_time = datetime.datetime.now()

    class DummyDBManager:
        def __init__(self):
            self.modules = {1: DummyModule(1, "core_system"), 2: DummyModule(2, "network_scanner")}
            self.files = {1: DummyFileHash(1, "main_loop.py"), 2: DummyFileHash(2, "packet_parser.py")}
            self.reports = [
                DummyReport(1, 1, 1, "completed", "Kritische Schwachstelle in Auth-Logik.", [
                    {"type": "vulnerability", "location": "auth.py:45", "detail": "SQL Injection in Login-Funktion"}
                ]),
                DummyReport(2, 2, 2, "in_progress", "Analyse des Scanners läuft.", [
                    {"type": "potential_dos", "location": "scanner.py:120", "detail": "Unbegrenzte Schleife"}
                ]),
                DummyReport(3, None, 1, "failed", "Analyse von main_loop.py fehlgeschlagen.", [
                    {"type": "error", "location": "main_loop.py:10", "detail": "Unexpected indent"}
                ]),
            ]

        def get_session(self): return self # Simuliert eine Session
        def close(self): pass

        def query(self, model):
            class DummyQuery:
                def filter_by(self, id):
                    if model == Module:
                        return self
                    elif model == FileHash:
                        return self
                    return self
                def first(self):
                    if model == Module:
                        return self.modules.get(id, None)
                    elif model == FileHash:
                        return self.files.get(id, None)
                    return None
            return DummyQuery()

        def get_code_analysis_reports(self, limit=50):
            return self.reports[:limit]
        
        # Vereinfachte Methoden für den __main__ Block
        def get_module_by_name(self, name): return self.modules.get(1 if name == "core_system" else 2)
        def add_module(self, **kwargs): pass
        def get_file_hash_by_filename(self, name): return self.files.get(1 if name == "main_loop.py" else 2)
        def add_file_hash(self, **kwargs): pass
        def add_code_analysis_report(self, **kwargs): pass


    # Ersetzen der tatsächlichen Imports durch Dummys für den Testfall
    from datetime import datetime
    CodeAnalysisReport = DummyReport
    Module = DummyModule
    FileHash = DummyFileHash
    DBManager = DummyDBManager

    # --- START DES TESTLAUFS ---
    root = tk.Tk()
    root.title("Jan's Eye Report Viewer Demo")
    root.geometry("900x600")
    root.configure(bg="#111111") # Dunkler Hintergrund für Cyber-Look

    # Dummy-Daten für den DBManager erstellen
    db_manager_instance = DBManager()

    viewer_plugin = JanEyeReportViewer()
    frame = viewer_plugin.create_gui(root)
    frame.pack(fill=tk.BOTH, expand=True)

    # Initialen GUI-Update aufrufen
    viewer_plugin.update_gui()

    root.mainloop()
