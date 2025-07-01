# plugins/jan_eye_report_viewer.py

import tkinter as tk
from tkinter import ttk
from plugins.gui_stream_base import GUIStreamPluginBase

# Importieren Sie den DBManager aus dem zentralen Tesseract-Backend
# Annahme: Ihr DBManager ist in einem Pfad wie 'tesseract_core.db_manager' verfügbar
# Für diesen Beispielcode wird ein direkter Import angenommen.

from db_manager_updated import DBManager, CodeAnalysisReport, Module, FileHash 


class JanEyeReportViewer(GUIStreamPluginBase):
	name = "Jan's Eye Reports"
	type = "analysis"
	stream_type = "report"
	description = "Zeigt Code-Analyseberichte von Jan's Eye an."
	author = "m4tt~h4ck"
	version = "1.0"

	def __init__(self):
		super().__init__():
		self.db_manager = DBManager() # Instanz des DBManager
		self.reports = [] # Liste zum Speichern der abgerufenen Berichte


	def create_gui(self, parent):

	"""

	Erstellt die GUI-Elemente für das Jan's Eye Report Viewer Plugin.

	"""

		frame = super().create_gui(parent) # Basis-Frame von GUIStreamPluginBase
		self.title_label = tk.Label(frame, text="Jan's Eye Code-Analyseberichte:", fg="#FFD700", bg="#222222", font=("Consolas", 14, "bold"))
		self.title_label.pack(pady=(10, 5))


# Treeview für die Berichtsübersicht

self.report_tree = ttk.Treeview(frame, 

columns=("ID", "Module", "File", "Status", "Time", "Summary"), 

show="headings", 

height=10)

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


self.report_tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)


# Scrollbar für die Treeview

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.report_tree.yview)

self.report_tree.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")


# Detailansicht für Findings

self.detail_label = tk.Label(frame, text="Detaillierte Findings:", 

fg="#00FFFF", bg="#222222", font=("Consolas", 11))

self.detail_label.pack(pady=(10, 2))

self.detail_text = tk.Text(frame, bg="#181818", fg="#FFFFFF", height=8, width=80, 

state="disabled", font=("Consolas", 10))

self.detail_text.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)


# Bindung für die Auswahl in der Treeview

self.report_tree.bind("<<TreeviewSelect>>", self.on_report_select)


# Refresh Button

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

self.reports = self.db_manager.get_code_analysis_reports(limit=50) # Die neuesten 50 Berichte abrufen


if not self.reports:

self.report_tree.insert("", tk.END, values=("", "", "", "", "", "Keine Berichte gefunden."))

return


for report in self.reports:

module_name = "N/A"

file_name = "N/A"


# Versuchen, den Modulnamen abzurufen

if report.module_id:

# Hier muss man eine Session für die Beziehung öffnen, da die ursprüngliche Session geschlossen ist

session = self.db_manager.get_session() 

try:

module = session.query(Module).filter_by(id=report.module_id).first()

if module:

module_name = module.name

except SQLAlchemyError as e:

print(f"Fehler beim Abrufen des Moduls für Bericht {report.id}: {e}")

finally:

session.close()


# Versuchen, den Dateinamen abzurufen

if report.file_hash_id:

session = self.db_manager.get_session()

try:

file_hash_entry = session.query(FileHash).filter_by(id=report.file_hash_id).first()

if file_hash_entry:

file_name = file_hash_entry.filename

except SQLAlchemyError as e:

print(f"Fehler beim Abrufen des FileHash für Bericht {report.id}: {e}")

finally:

session.close()

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


report_id = int(item_values[0]) # Die ID des ausgewählten Berichts


# Den vollständigen Bericht aus der Liste der abgerufenen Berichte finden

selected_report = next((r for r in self.reports if r.id == report_id), None)


if selected_report and selected_report.findings:

findings_str = ""

for finding in selected_report.findings:

findings_str += f"Type: {finding.get('type', 'N/A')}\n"

findings_str += f"Location: {finding.get('location', 'N/A')}\n"

findings_str += f"Detail: {finding.get('detail', 'N/A')}\n\n"

self.detail_text.config(state="normal")

self.detail_text.delete(1.0, tk.END)

self.detail_text.insert(tk.END, findings_str.strip())

self.detail_text.config(state="disabled")

else:

self.detail_text.config(state="normal")

self.detail_text.delete(1.0, tk.END)

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

# Dies ist ein eigenständiger Testlauf für das Plugin.

# In der echten Tesseract-Anwendung würde es vom Haupt-Metavisualizer geladen.

root = tk.Tk()

root.title("Jan's Eye Report Viewer Demo")

root.geometry("900x600")

root.configure(bg="#111111") # Dunkler Hintergrund für Cyber-Look


# Dummy-Daten für den DBManager erstellen, falls nicht vorhanden

db_manager_instance = DBManager()

# Sicherstellen, dass Module und FileHashes für die Verknüpfung existieren

module_name_1 = "core_system"

module_name_2 = "network_scanner"

file_name_1 = "main_loop.py"

file_name_2 = "packet_parser.py"


mod1 = db_manager_instance.get_module_by_name(module_name_1)

if not mod1:

db_manager_instance.add_module(name=module_name_1, description="Kernsystem-Module")

mod1 = db_manager_instance.get_module_by_name(module_name_1)


mod2 = db_manager_instance.get_module_by_name(module_name_2)

if not mod2:

db_manager_instance.add_module(name=module_name_2, description="Netzwerk-Scanner-Modul")

mod2 = db_manager_instance.get_module_by_name(module_name_2)


file1 = db_manager_instance.get_file_hash_by_filename(file_name_1)

if not file1:

db_manager_instance.add_file_hash(filename=file_name_1, sha256="hash123abc")

file1 = db_manager_instance.get_file_hash_by_filename(file_name_1)


file2 = db_manager_instance.get_file_hash_by_filename(file_name_2)

if not file2:

db_manager_instance.add_file_hash(filename=file_name_2, sha256="hash456def")

file2 = db_manager_instance.get_file_hash_by_filename(file_name_2)


# Fügen Sie einige Dummy-Berichte hinzu, wenn die DB leer ist

if not db_manager_instance.get_code_analysis_reports(limit=1):

db_manager_instance.add_code_analysis_report(

module_id=mod1.id,

file_hash_id=file1.id,

status="completed",

summary="Kritische Schwachstelle in Authentifizierungslogik gefunden.",

findings=[

{"type": "vulnerability", "location": "auth.py:45", "detail": "SQL Injection in Login-Funktion"},

{"type": "recommendation", "location": "auth.py", "detail": "Parameterisierte Queries verwenden"}

],

ai_model_version="Jan's Eye v0.2-beta"

)

db_manager_instance.add_code_analysis_report(

module_id=mod2.id,

file_hash_id=file2.id,

status="in_progress",

summary="Analyse des Netzwerk-Scanners läuft: Potenzielle DoS-Vektoren.",

findings=[

{"type": "potential_dos", "location": "scanner.py:120", "detail": "Unbegrenzte Schleife bei Paketverarbeitung"},

{"type": "info", "location": "config.py", "detail": "Verwendet Standard-Port 8080"}

],

ai_model_version="Jan's Eye v0.2-beta"

)

db_manager_instance.add_code_analysis_report(

file_hash_id=file1.id,

status="failed",

summary="Analyse von main_loop.py fehlgeschlagen: Syntaxfehler.",

findings=[

{"type": "error", "location": "main_loop.py:10", "detail": "Unexpected indent"}

],

ai_model_version="Jan's Eye v0.2-beta"

)


viewer_plugin = JanEyeReportViewer()

frame = viewer_plugin.create_gui(root)

frame.pack(fill=tk.BOTH, expand=True)


# Initialen GUI-Update aufrufen

viewer_plugin.update_gui()


root.mainloop()


