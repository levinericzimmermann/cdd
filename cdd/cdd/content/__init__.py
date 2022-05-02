import pkgutil

from cdd import configurations

__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module_test_name = module_name.split('.')[0]
    if module_test_name in configurations.CHAPTER_TO_RENDER_TUPLE:
        __all__.append(module_name)
        _module = loader.find_module(module_name).load_module(module_name)
        globals()[module_name] = _module
