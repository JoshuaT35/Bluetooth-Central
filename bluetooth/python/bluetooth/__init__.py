from .bluetooth import start_ble_stream


__doc__ = bluetooth.__doc__
if hasattr(bluetooth, "__all__"):
    __all__ = bluetooth.__all__
