import importlib
import pkgutil
import inspect
import logging

logger = logging.getLogger(__name__)


def discover_transformers(base_paths):
    """
    Discover all transformer classes in the specified package.

    Args:
        base_paths (list): List of package paths to search for transformers.

    Returns:
        dict: A dictionary mapping transformer names to their import paths.
    """
    transformers = {}

    for path in base_paths:
        try:
            package = importlib.import_module(path)
        except ImportError as e:
            # Only log debug message for missing modules - they're expected
            logger.debug(f"Module {path} not found: {e}")
            continue

        try:
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
                            logger.info(f"Discovered transformer: {name} -> {key}")
                except Exception as e:
                    logger.debug(f"Could not import module {module_name}: {e}")
                    continue
        except AttributeError:
            # Package doesn't have __path__ (not a package)
            logger.debug(f"Path {path} is not a package")
            continue

    return transformers
