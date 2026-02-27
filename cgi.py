import sys
import re
from email.message import Message

# Re-implementation of cgi.valid_boundary for Python 3.13 compatibility
_vb_pattern = re.compile(b'^[ -~]{0,200}[!-~]$')

def valid_boundary(s):
    if s is None:
        return False
    if isinstance(s, str):
        s = s.encode('ascii', errors='replace')
    return _vb_pattern.match(s)

def parse_header(line):
    """
    Parse a Content-type like header.
    Return the main content-type and a dictionary of parameters.
    """
    if line is None:
        return None, {}
    if isinstance(line, bytes):
        line = line.decode('iso-8859-1')
    m = Message()
    m['content-type'] = line
    return m.get_content_type(), m.get_params({}, header='content-type', unquote=True) or {}

def parse_multipart(fp, pdict):
    """
    Parse multipart input.
    """
    raise NotImplementedError("cgi.parse_multipart not implemented in shim")

# Mock other attributes if necessary
log = lambda *args: None

# Register this module as 'cgi' in sys.modules
sys.modules['cgi'] = sys.modules[__name__]
