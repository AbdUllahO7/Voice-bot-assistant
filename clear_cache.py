#!/usr/bin/env python3
"""
Clear Python cache that might be interfering with config loading
"""

import os
import shutil
import glob

def clear_python_cache():
    print("🧹 Clearing Python Cache")
    print("=" * 30)
    
    # Remove __pycache__ directories
    cache_dirs = glob.glob('**/__pycache__', recursive=True)
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"✅ Removed {cache_dir}")
    
    # Remove .pyc files
    pyc_files = glob.glob('**/*.pyc', recursive=True)
    for pyc_file in pyc_files:
        if os.path.exists(pyc_file):
            os.remove(pyc_file)
            print(f"✅ Removed {pyc_file}")
    
    # Remove .pyo files  
    pyo_files = glob.glob('**/*.pyo', recursive=True)
    for pyo_file in pyo_files:
        if os.path.exists(pyo_file):
            os.remove(pyo_file)
            print(f"✅ Removed {pyo_file}")
    
    if not cache_dirs and not pyc_files and not pyo_files:
        print("✅ No cache files found to remove")
    
    print("\n🎯 Cache cleared! Try running the main application now.")
    print("   python whisper_voice_bot.py")

if __name__ == "__main__":
    clear_python_cache()