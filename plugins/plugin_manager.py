# plugins/meta_plugin_inspector.py

import tkinter as tk
from plugins.gui_stream_base import GUIStreamPluginBase

class MetaPluginInspector(GUIStreamPluginBase):
    name = "Meta Plugin Inspector"
    type = "meta"
    stream_type = "meta"
    description = "Visualisiert und inspiziert alle geladenen Plugins – ein Plugin für Plugins."
    author = "m4tt~h4ck"
    version = "1.0"

    def __init__(self):
        super().__init__()
        self.plugin_manager = None  # Wird später gesetzt

    def create_gui(self, parent):
        frame = super().create_gui(parent)
        self.title_label = tk.Label(frame, text="Geladene Plugins:", fg="#00FFCC", bg="#222222", font=("Consolas", 14, "bold"))
        self.title_label.pack(pady=(10, 5))

        self.listbox = tk.Listbox(frame, bg="#181818", fg="#00FF00", font=("Consolas", 11), width=60, height=10)
        self.listbox.pack(padx=10, pady=5)

        self.meta_label = tk.Label(frame, text="Metadaten:", fg="#FF00FF", bg="#222222", font=("Consolas", 11))
        self.meta_label.pack(pady=(10, 2))
        self.meta_text = tk.Text(frame, bg="#181818", fg="#FFFFFF", height=6, width=60, state="disabled", font=("Consolas", 10))
        self.meta_text.pack(padx=10, pady=(0,10))

        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        return frame

    def update_gui(self, data=None):
        if not self.plugin_manager:
            return
        self.listbox.delete(0, tk.END)
        for pname, plugin in self.plugin_manager.plugins.items():
            self.listbox.insert(tk.END, f"{plugin.name} [{plugin.type}]")

    def on_select(self, event):
        if not self.plugin_manager:
            return
        selection = self.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        pname = list(self.plugin_manager.plugins.keys())[idx]
        plugin = self.plugin_manager.plugins[pname]
        meta = (
            f"Name: {plugin.name}\n"
            f"Typ: {plugin.type}\n"
            f"Beschreibung: {plugin.description}\n"
            f"Autor: {getattr(plugin, 'author', 'unbekannt')}\n"
            f"Version: {getattr(plugin, 'version', 'unbekannt')}\n"
            f"Aktiviert: {getattr(plugin, 'enabled', True)}"
        )
        self.meta_text.config(state="normal")
        self.meta_text.delete(1.0, tk.END)
        self.meta_text.insert(tk.END, meta)
        self.meta_text.config(state="disabled")

    def run(self, plugin_manager=None):
        """
        Setzt den PluginManager und aktualisiert die GUI.
        """
        self.plugin_manager = plugin_manager
        if self.gui_frame:
            self.update_gui()

# --- Beispiel für die Einbindung in die Hauptanwendung ---

if __name__ == "__main__":
    # Annahme: PluginManager und Tkinter-App existieren bereits
    import tkinter as tk
    from plugins.plugin_manager import PluginManager

    root = tk.Tk()
    root.title("Meta Plugin Inspector Demo")
    pm = PluginManager()
    pm.load_plugins()

    plugin = MetaPluginInspector()
    plugin.run(plugin_manager=pm)
    frame = plugin.create_gui(root)
    frame.pack(fill=tk.BOTH, expand=True)
    plugin.update_gui()

    root.mainloop()
