#!/usr/bin/env python3
"""
Simple test script for EzProject Discord Bot
Tests basic functionality without database connection
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import discord
        from discord.ext import commands
        print("✅ Discord.py imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Discord.py import failed: {e}")
        return False

def test_config():
    """Test configuration values"""
    try:
        from config import BOT_TOKEN, MONGODB_URI, EMBED_COLORS
        print("✅ Configuration loaded successfully!")
        
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

def test_file_structure():
    """Test if all required files exist"""
    required_files = [
        "main.py",
        "commands.py", 
        "slash_commands.py",
        "hosting_setup.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "Datamodule/db.py",
        "Datamodule/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present!")
        return True

def test_basic_bot_creation():
    """Test if we can create a basic bot instance"""
    try:
        import discord
        from discord.ext import commands
        
        intents = discord.Intents.default()
        # Remove message_content for older discord.py versions
        # intents.message_content = True
        
        bot = commands.Bot(command_prefix="!", intents=intents)
        print("✅ Bot instance created successfully!")
        return True
    except Exception as e:
        print(f"❌ Bot creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Simple EzProject Bot Tests...\n")
    
    tests = [
        ("File Structure Test", test_file_structure),
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Bot Creation Test", test_basic_bot_creation),
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
        print("🎉 All basic tests passed! Your bot setup is correct.")
        print("\nNext steps:")
        print("1. Check your MongoDB connection string")
        print("2. Verify your Discord bot token")
        print("3. Run 'python slash_commands.py' to start the bot")
        print("4. Or run 'python commands.py' for prefix commands")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 