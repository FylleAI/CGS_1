#!/usr/bin/env python3
"""
Start backend with AI-powered KBA transformer.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import uvicorn
from api.rest.main import app

if __name__ == "__main__":
    print("🚀 Starting CGS Backend with AI-powered KBA transformer...")
    print("🤖 Real AI integration enabled!")
    print("💰 Cost tracking enabled!")
    print("🔗 Server will be available at: http://localhost:8000")
    print("📚 KBA API endpoints: http://localhost:8000/api/v1/kba/")
    print()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info",
        reload=False
    )
