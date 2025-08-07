#!/usr/bin/env python3
"""
Debug script to check configuration loading
Run this to see what's happening with your config.py
"""

import os
import sys

def debug_config():
    print("🔍 Debugging Configuration Loading")
    print("=" * 50)
    
    # Check if config.py exists
    print(f"1. Current directory: {os.getcwd()}")
    print(f"2. Files in directory: {os.listdir('.')}")
    print(f"3. config.py exists: {os.path.exists('config.py')}")
    
    if os.path.exists('config.py'):
        print("4. config.py file size:", os.path.getsize('config.py'), "bytes")
    
    # Try to import config
    print("\n5. Trying to import config...")
    try:
        import config
        print("✅ Config import successful!")
        
        # Check if OPENAI_API_KEY exists
        if hasattr(config, 'OPENAI_API_KEY'):
            api_key = getattr(config, 'OPENAI_API_KEY')
            print(f"✅ OPENAI_API_KEY found")
            print(f"   Length: {len(api_key)} characters")
            print(f"   Starts with: {api_key[:10]}...")
            print(f"   Is placeholder: {api_key == 'your-openai-api-key-here'}")
            print(f"   Is valid format: {api_key.startswith('sk-')}")
        else:
            print("❌ OPENAI_API_KEY not found in config")
            
        # Check Google Cloud path
        if hasattr(config, 'GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH'):
            path = getattr(config, 'GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH')
            print(f"✅ GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH found")
            print(f"   Path: {path}")
            print(f"   File exists: {os.path.exists(path)}")
        else:
            print("❌ GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH not found")
            
        # Show all config attributes
        print("\n6. All config attributes:")
        for attr in dir(config):
            if not attr.startswith('__'):
                value = getattr(config, attr)
                if 'KEY' in attr or 'PATH' in attr:
                    # Mask sensitive data
                    if isinstance(value, str) and len(value) > 10:
                        masked = value[:10] + "..." + value[-4:]
                    else:
                        masked = value
                    print(f"   {attr} = {masked}")
                else:
                    print(f"   {attr} = {value}")
                    
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
    except Exception as e:
        print(f"❌ Error loading config: {e}")

if __name__ == "__main__":
    debug_config()