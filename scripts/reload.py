from scripts.client import Client

intro = """
For development:

%load_ext autoreload
%autoreload 2


Run this in REPL so that its the same as --reload for uvicorn and can develop
instance methods!
"""

c = Client()
print(intro)
print(c)
