#!/usr/bin/env python3
"""
Test script for EzProject Discord Bot
This script tests basic functionality without running the full bot
"""

import sys
import os
from pymongo import MongoClient
from config.config import MONGODB_URI, DATABASE_NAME, COLLECTION_NAME, BOT_TOKEN, EMBED_COLORS

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        client = MongoClient(MONGODB_URI)
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Test basic operations
        test_doc = {"test": "connection", "timestamp": "test"}
        result = collection.insert_one(test_doc)
        print(f"✅ Database write test successful! Inserted ID: {result.inserted_id}")
        
        # Clean up test document
        collection.delete_one({"_id": result.inserted_id})
        print("✅ Database cleanup successful!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import discord
        from discord.ext import commands
        from db.db import add, list_task, edit, delete_task, delete_project
        from config.config import BOT_TOKEN, EMBED_COLORS
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration values"""
    try:
        from config.config import BOT_TOKEN, MONGODB_URI
        if BOT_TOKEN and BOT_TOKEN != "your_bot_token_here":
            print("✅ Bot token configured!")
        else:
            print("⚠️  Bot token not configured (using default)")
        
        if MONGODB_URI and "mongodb+srv://" in MONGODB_URI:
            print("✅ MongoDB URI configured!")
        else:
            print("⚠️  MongoDB URI not configured (using default)")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running EzProject Bot Tests...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("MongoDB Connection Test", test_mongodb_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot is ready to run.")
        print("\nNext steps:")
        print("1. Run 'python slash_commands.py' to start the bot with slash commands")
        print("2. Run 'python commands.py' to start the bot with prefix commands")
        print("3. Run 'python hosting_setup.py' for production deployment")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 