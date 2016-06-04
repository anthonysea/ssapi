import os
import sys
from api.api import app

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

if __name__ == '__main__':
    app.run(debug=True)