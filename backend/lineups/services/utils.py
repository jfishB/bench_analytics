"""Helper functions for lineup services."""


def get(obj, name, default=None):
    """Helper to read either dataclass attributes or dict keys."""
    if obj is None:
        return default
    if hasattr(obj, name):
        return getattr(obj, name)
    if isinstance(obj, dict):
        return obj.get(name, default)
    return default
