#!/usr/bin/env python3
"""
Quick Fix Script for Joe's Restaurant Voice Ordering System
This script will help diagnose and fix configuration issues.
"""

import os
import sys

def main():
    print("🔧 Quick Fix - Joe's Restaurant Configuration")
    print("=" * 50)
    
    # Step 1: Check if we're in the right directory
    print("1. Checking current directory...")
    cwd = os.getcwd()
    print(f"   Current directory: {cwd}")
    
    # Check for main file
    if not os.path.exists('whisper_voice_bot.py'):
        print("❌ whisper_voice_bot.py not found!")
        print("   Please run this script from the project directory")
        return
    print("✅ Found main application file")
   
    
    # Step 3: Check for config.py
    print("\n3. Checking for config.py...")
    if not os.path.exists('config.py'):
        print("❌ config.py not found!")
        print("   Creating config.py from template...")
        
        # Copy template to config.py
        try:
            with open('config_template.py', 'r') as template:
                content = template.read()
            with open('config.py', 'w') as config:
                config.write(content)
            print("✅ Created config.py from template")
        except Exception as e:
            print(f"❌ Failed to create config.py: {e}")
            return
    else:
        print("✅ Found config.py")
    
    # Step 4: Test config import
    print("\n4. Testing config import...")
    try:
        import config
        print("✅ Config import successful")
        
        # Check API key
        if hasattr(config, 'OPENAI_API_KEY'):
            api_key = config.OPENAI_API_KEY
            if api_key == "your-openai-api-key-here":
                print("⚠️  OpenAI API key is still placeholder")
                print("   Please edit config.py and add your real API key")
            elif api_key.startswith('sk-'):
                print(f"✅ OpenAI API key looks valid (length: {len(api_key)})")
            else:
                print("❌ OpenAI API key format looks incorrect")
                print("   Should start with 'sk-'")
        else:
            print("❌ OPENAI_API_KEY not found in config.py")
        
        # Check Google Cloud path
        if hasattr(config, 'GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH'):
            path = config.GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH
            if os.path.exists(path):
                print(f"✅ Google Cloud service account file found")
            else:
                print(f"⚠️  Google Cloud service account file not found: {path}")
                print("   Please check the path in config.py")
        else:
            print("❌ GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH not found in config.py")
            
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Step 5: Test OpenAI connection
    print("\n5. Testing OpenAI connection...")
    try:
        import openai
        if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY.startswith('sk-'):
            client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            models = client.models.list()
            model_ids = [m.id for m in models.data if 'gpt' in m.id]
            if model_ids:
                print(f"✅ OpenAI connection successful! Available GPT models: {len(model_ids)}")
            else:
                print("⚠️  Connected but no GPT models available")
        else:
            print("⚠️  Skipping OpenAI test - API key not configured")
    except ImportError:
        print("⚠️  OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. If config.py was created, edit it with your real API keys")
    print("2. Get OpenAI API key: https://platform.openai.com/api-keys")
    print("3. Get Google Cloud credentials: https://console.cloud.google.com/")
    print("4. Run the main application: python whisper_voice_bot.py")
    print("=" * 50)

if __name__ == "__main__":
    main()