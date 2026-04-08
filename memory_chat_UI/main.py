# This file serves as the entry point for Uvicorn
# It imports the app from the chatapi module so `uvicorn main:app` works correctly.

from chatapi.main import app
