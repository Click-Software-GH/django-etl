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
        logger.info(f"Searching for transformers in: {path}")
        try:
            package = importlib.import_module(path)
            logger.info(f"Successfully imported package: {path}")
        except ImportError as e:
            # Only log debug message for missing modules - they're expected
            logger.debug(f"Module {path} not found: {e}")
            continue

        try:
            logger.info(f"Package {path} has __path__: {hasattr(package, '__path__')}")
            if hasattr(package, "__path__"):
                logger.info(f"Package path: {package.__path__}")

            for _, module_name, ispkg in pkgutil.walk_packages(
                package.__path__, package.__name__ + "."
            ):
                logger.info(f"Found module: {module_name}, is_package: {ispkg}")
                if ispkg:
                    continue
                try:
                    module = importlib.import_module(module_name)
                    logger.info(f"Successfully imported module: {module_name}")

                    # Log all classes found in the module
                    classes_found = [
                        name
                        for name, obj in inspect.getmembers(module)
                        if inspect.isclass(obj)
                    ]
                    logger.info(f"Classes found in {module_name}: {classes_found}")

                    for name, obj in inspect.getmembers(module):
                        logger.debug(f"Examining member: {name}, type: {type(obj)}")
                        if (
                            name.endswith("Transformer")
                            and inspect.isclass(obj)
                            and name != "BaseTransformer"
                        ):  # Exclude the base class
                            key = name.replace("Transformer", "").lower()
                            transformers[key] = obj
                            logger.info(f"Discovered transformer: {name} -> {key}")
                except Exception as e:
                    logger.error(f"Could not import module {module_name}: {e}")
                    continue
        except AttributeError:
            # Package doesn't have __path__ (not a package)
            logger.debug(f"Path {path} is not a package")
            continue

    logger.info(f"Total transformers discovered: {len(transformers)}")
    return transformers
