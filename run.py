#!/usr/bin/env python3
"""
Main entry point for the Solar Analysis API application.
Run with: python run.py
"""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    # Use reload=False for production
    reload = os.environ.get("ENV", "production") == "development"

    uvicorn.run(
        "src.api.main:app", host=host, port=port, reload=reload, log_level="info"
    )
