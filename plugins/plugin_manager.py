# plugins/plugin_manager.py

import os
import importlib
import inspect

class PluginBase:
    name = "UnnamedPlugin"
    type = "generic"
    description = "No description provided."
    author = "Unknown"
    version = "1.0"
    enabled = True

    def run(self, *args, **kwargs):
        raise NotImplementedError("Plugin must implement run() method")


class PluginManager:
    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = {}  # dict: name -> PluginBase instance

    def load_plugins(self):
        """
        Lädt alle Plugins aus dem plugins_dir,
        die von PluginBase erben (außer PluginBase selbst).
        """
        self.plugins.clear()
        for fname in os.listdir(self.plugins_dir):
            if (
                fname.endswith(".py")
                and not fname.startswith("__")
                and fname != "plugin_manager.py"
            ):
                modulename = f"{self.plugins_dir}.{fname[:-3]}"
                try:
                    module = importlib.import_module(modulename)
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(obj, PluginBase)
                            and obj is not PluginBase
                        ):
                            instance = obj()
                            if instance.enabled:
                                self.plugins[instance.name] = instance
                except Exception as e:
                    print(f"[Error] Failed to load plugin '{modulename}': {e}")

    def get_plugin(self, name):
        """Gibt das Plugin mit dem angegebenen Namen zurück oder None."""
        return self.plugins.get(name)

    def get_plugins_by_type(self, ptype):
        """Gibt eine Liste aller Plugins eines bestimmten Typs zurück."""
        return [p for p in self.plugins.values() if p.type == ptype and p.enabled]

    def list_plugins(self):
        """Listet alle geladenen Plugins mit Name, Typ und Beschreibung auf."""
        for p in self.plugins.values():
            print(f"- {p.name} (Typ: {p.type}, Version: {p.version})\n  {p.description}")

    def run_plugin(self, name, *args, **kwargs):
        """
        Führt ein Plugin per Name aus mit optionalen Parametern.
        Gibt das Ergebnis zurück oder None, falls nicht gefunden.
        """
        plugin = self.get_plugin(name)
        if plugin:
            return plugin.run(*args, **kwargs)
        else:
            print(f"[Warning] Plugin '{name}' nicht gefunden.")
            return None
