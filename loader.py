### UE6-Integration später möglich via socket.send(json.dumps(features)).
import importlib

OPTIONAL_MODULES = {
    "scapy": "scapy.all",
    "requests": "requests",
    "subprocess": "subprocess",
    "fcntl": "fcntl",
    "socket": "socket"
}

def load_optional_modules(modules_to_load=None):
    """
    Lädt optional verfügbare Module dynamisch.

    Args:
        modules_to_load (dict): Optional, dict mit name->modulpfad. 
                                Standard ist OPTIONAL_MODULES.

    Returns:
        dict: key = Modulname, value = importiertes Modul oder None.
    """
    if modules_to_load is None:
        modules_to_load = OPTIONAL_MODULES

    loaded_modules = {}
    for name, module_path in modules_to_load.items():
        try:
            loaded_modules[name] = importlib.import_module(module_path)
        except ImportError:
            loaded_modules[name] = None
    return loaded_modules


# Beispiel:
if __name__ == "__main__":
    modules = load_optional_modules()
    if modules["scapy"]:
        print("Scapy ist verfügbar")
    else:
        print("Scapy nicht installiert")
