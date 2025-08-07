#!/usr/bin/env python3
"""
Test the exact same logic that the main application uses
This will help identify where the disconnect is happening.
"""

import logging

# Set up logging exactly like main app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_main_app_logic():
    print("🧪 Testing Main Application Logic")
    print("=" * 50)
    
    # Step 1: Import config (exactly like main app)
    try:
        import importlib
        if 'config' in globals():
            importlib.reload(config)
        else:
            import config
        CONFIG_LOADED = True
        logger.info("✅ Configuration loaded successfully")
        
        # Immediate validation
        if hasattr(config, 'OPENAI_API_KEY'):
            api_key_preview = config.OPENAI_API_KEY[:15] + "..." if len(config.OPENAI_API_KEY) > 15 else config.OPENAI_API_KEY
            logger.info(f"🔑 API Key loaded: {api_key_preview} (length: {len(config.OPENAI_API_KEY)})")
        else:
            logger.error("❌ OPENAI_API_KEY not found in config")
            
    except ImportError as e:
        CONFIG_LOADED = False
        logger.error(f"❌ config.py not found: {e}")
        print("⚠️  config.py not found!")
        return
    except Exception as e:
        CONFIG_LOADED = False
        logger.error(f"❌ Error loading config.py: {e}")
        print(f"⚠️  Error loading config.py: {e}")
        return
    
    # Step 2: Load API key (exactly like main app)
    if CONFIG_LOADED:
        openai_api_key = getattr(config, 'OPENAI_API_KEY', 'your-openai-api-key-here')
        
        # Debug logging
        logger.info(f"📝 Config loaded - API key length: {len(openai_api_key)} chars")
        logger.info(f"📝 API key starts with: {openai_api_key[:10]}...")
        
    else:
        openai_api_key = 'your-openai-api-key-here'
        print("❌ Config not loaded, using placeholder")
        return
    
    # Step 3: Check GPT enabled (exactly like main app)
    gpt_enabled = bool(openai_api_key and 
                       openai_api_key != "your-openai-api-key-here" and 
                       openai_api_key.startswith('sk-'))
    
    logger.info(f"🤖 GPT enabled check: API key valid = {gpt_enabled}")
    
    # Step 4: Detailed breakdown
    print("\n🔍 Detailed Analysis:")
    print(f"   API key exists: {bool(openai_api_key)}")
    print(f"   API key is not placeholder: {openai_api_key != 'your-openai-api-key-here'}")
    print(f"   API key starts with sk-: {openai_api_key.startswith('sk-')}")
    print(f"   Combined result: {gpt_enabled}")
    
    if not gpt_enabled:
        print("\n❌ GPT would be DISABLED")
        logger.warning("⚠️  GPT integration disabled - please check your OpenAI API key in config.py")
    else:
        print("\n✅ GPT would be ENABLED")
        
        # Step 5: Test OpenAI connection (like main app)
        try:
            import openai
            openai_client = openai.OpenAI(api_key=openai_api_key)
            
            # Test connection
            models_response = openai_client.models.list()
            all_models = [model.id for model in models_response.data]
            
            # Check which GPT models are available
            preferred_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            available_models = [model for model in preferred_models if model in all_models]
            
            if available_models:
                logger.info(f"✅ GPT integration would be enabled with models: {', '.join(available_models)}")
                print(f"✅ Available models: {', '.join(available_models)}")
            else:
                print("⚠️  No compatible GPT models found")
                
        except Exception as e:
            print(f"❌ OpenAI connection failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Result: GPT would be", "ENABLED ✅" if gpt_enabled else "DISABLED ❌")
    print("=" * 50)

if __name__ == "__main__":
    test_main_app_logic()