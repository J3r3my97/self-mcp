import os
import sys

import uvicorn

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    # Start the FastAPI app
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=False) 