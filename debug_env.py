import sys
print(sys.version)
try:
    import cgi
    print("cgi module found")
except ImportError as e:
    print(e)

try:
    import django
    print(f"Django version: {django.get_version()}")
except ImportError as e:
    print(e)
