#!/usr/bin/env python3
"""
Quick Database Seeding Script
==============================
Run this from the root directory to seed the database with comprehensive data.

This is a convenience wrapper around backend/scripts/comprehensive_seed_data.py
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import and run the main seed script
os.chdir(backend_path)

from scripts.comprehensive_seed_data import main
import asyncio

if __name__ == "__main__":
    print("🚀 Starting Database Seeding...")
    print("This will create/update comprehensive data for amits.joys@gmail.com")
    print()
    
    asyncio.run(main())
