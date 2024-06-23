import sys
import os

# Dodaj ścieżkę do katalogu projektu
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import project
print("Attributes of project module:", dir(project))  # Debugowanie

from project import app

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=os.environ.get("DEBUG") == 'True')
