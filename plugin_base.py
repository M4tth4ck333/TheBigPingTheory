class PluginBase:
    def run(self, *args, **kwargs):
        raise NotImplementedError("Plugin muss run() implementieren")
