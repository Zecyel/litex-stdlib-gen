try:
    import pyperclip
except ImportError:
    pyperclip = None

def read_clipboard():
    """Read text from clipboard. Returns string or None if unsupported."""
    if not pyperclip:
        raise ImportError("pyperclip not installed. Run: pip install pyperclip")
    try:
        return pyperclip.paste()
    except pyperclip.PyperclipException:
        return None

def write_clipboard(text):
    """Write text to clipboard. Returns True if successful."""
    if not pyperclip:
        raise ImportError("pyperclip not installed. Run: pip install pyperclip")
    try:
        pyperclip.copy(str(text))
        return True
    except pyperclip.PyperclipException:
        return False
