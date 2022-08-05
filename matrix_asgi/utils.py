"""Utility functions."""
import asyncio
import importlib


def get_application(application_name):
    """Load a callable from a `module.submodule:Object.callable` string.

    copy-paste from https://github.com/sivulich/mqttasgi/blob/master/mqttasgi/utils.py
    """
    module_path, object_path = application_name.split(":", 1)
    application = importlib.import_module(module_path)
    for bit in object_path.split("."):
        application = getattr(application, bit)

    return application


def terminate(event, signal):  # pragma: no cover
    """Close handling stuff."""
    event.set()
    asyncio.get_running_loop().remove_signal_handler(signal)
