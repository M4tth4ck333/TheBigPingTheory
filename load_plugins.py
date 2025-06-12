# load_plugins.py
import os
import importlib

def load_plugins():
    plugins = []
    plugins_dir = "plugins"
    for fname in os.listdir(plugins_dir):
        if fname.endswith(".py") and not fname.startswith("__"):
            modulename = f"{plugins_dir}.{fname[:-3]}"
            module = importlib.import_module(modulename)
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type):
                    plugins.append(obj())
    return plugins
