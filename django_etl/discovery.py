import importlib
import pkgutil
import inspect


def discover_transformers(base_paths):
    """
    Discover all transformer classes in the specified package.

    Args:
        package_name (str): The name of the package to search for transformers.

    Returns:
        dict: A dictionary mapping transformer names to their import paths.
    """
    transformers = {}

    for path in base_paths:
        try:
            package = importlib.import_module(path)
        except ImportError as e:
            print(f"Error importing package {path}: {e}")
            continue

        for _, module_name, ispkg in pkgutil.walk_packages(
            package.__path__, package.__name__ + "."
        ):
            if ispkg:
                continue
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if (
                        name.endswith("Transformer")
                        and inspect.isclass(obj)
                        and name != "BaseTransformer"
                    ):  # Exclude the base class
                        key = name.replace("Transformer", "").lower()
                        transformers[key] = obj
            except Exception:
                continue

    return transformers
