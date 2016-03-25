import __builtin__
import io
import os

_open = __builtin__.open

def fake_open(path, *args, **kwargs):
    if path.endswith(os.path.join('openpyxl', '.constants.json')):
        return io.BytesIO(b'''{"__author__": "", "__author_email__": "", "__license__": "",\
                "__maintainer_email__": "", "__url__": "", "__version__": ""}''')
    return _open(path, *args, **kwargs)

def ignore_openpyxl_constants(*__):
    __builtin__.open = fake_open
    __import__('openpyxl')  # read .constants.json by fake_open().
    __builtin__.open = _open
