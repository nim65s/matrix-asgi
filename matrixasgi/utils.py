import asyncio
import importlib
import sys


def get_application(application_name):
    # copy-paste from https://github.com/sivulich/mqttasgi/blob/master/mqttasgi/utils.py
    sys.path.insert(0, ".")
    module_path, object_path = application_name.split(":", 1)
    application = importlib.import_module(module_path)
    for bit in object_path.split("."):
        application = getattr(application, bit)

    return application


def terminate(self, event, signal):
    """Close handling stuff."""
    event.set()
    asyncio.get_running_loop().remove_signal_handler(signal)
