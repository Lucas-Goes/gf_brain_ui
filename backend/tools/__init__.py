from pathlib import Path
import importlib
import inspect
import pkgutil


def discover_tools():
    tools = {}
    package_dir = Path(__file__).parent
    for module_info in pkgutil.iter_modules([str(package_dir)]):
        if module_info.name == "base" or module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f".{module_info.name}", package=__package__)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue
            if obj.name and hasattr(obj, "run"):
                tools[obj.name] = obj
    return tools
