
import sys
from imp import reload

default_unicode = 'utf-8'

ansi = not sys.platform.startswith("win")

def setup_console(sys_enc=default_unicode):
    """
    Set sys.defaultencoding to `sys_enc` and update stdout/stderr writers to corresponding encoding
    .. note:: For Win32 the OEM console encoding will be used istead of `sys_enc`
    http://habrahabr.ru/post/117236/
    http://www.py-my.ru/post/4bfb3c6a1d41c846bc00009b
    """
    global ansi
    reload(sys)
    
    try:
        if sys.platform.startswith("win"):
            import ctypes
            enc = "cp%d" % ctypes.windll.kernel32.GetOEMCP()
        else:
            enc = (sys.stdout.encoding if sys.stdout.isatty() else
                        sys.stderr.encoding if sys.stderr.isatty() else
                            sys.getfilesystemencoding() or sys_enc)

        sys.setdefaultencoding(sys_enc)

        if sys.stdout.isatty() and sys.stdout.encoding != enc:
            sys.stdout = codecs.getwriter(enc)(sys.stdout, 'replace')

        if sys.stderr.isatty() and sys.stderr.encoding != enc:
            sys.stderr = codecs.getwriter(enc)(sys.stderr, 'replace')
    except:
        pass

def _imports():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            yield val.__name__
