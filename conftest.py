def pytest_ignore_collect(collection_path, config):
    """
    Ignore __init__.py files during test collection.
    """
    return collection_path.name == "__init__.py"
