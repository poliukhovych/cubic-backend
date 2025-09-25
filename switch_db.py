"""
Script for quick switching between local and Docker database
"""

import os
import sys
from pathlib import Path


def switch_database(target: str):
    """Switch between local and Docker database"""
    
    if target not in ["local", "docker"]:
        print("❌ Error: Use 'local' or 'docker'")
        print("Examples:")
        print("  python switch_db.py local")
        print("  python switch_db.py docker")
        return False
    
    project_root = Path(__file__).parent
    env_file = project_root / "env"
    source_file = project_root / f"env.{target}"
    
    if not source_file.exists():
        print(f"❌ Error: File {source_file} not found")
        return False
    
    try:
        with open(source_file, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(env_file, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"✅ Successfully switched to {target} database")
        print(f"📁 Used file: {source_file}")
        
        try:
            from app.core.config import settings
            print(f"🔗 DATABASE_URL: {settings.database_url}")
        except Exception as e:
            print(f"⚠️  Failed to load configuration: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during switching: {e}")
        return False


def show_current_config():
    """Show current database configuration"""
    try:
        from app.core.config import settings
        print("📊 Current database configuration:")
        print(f"🔗 DATABASE_URL: {settings.database_url}")
        
        if "localhost" in settings.database_url:
            print("🏠 Mode: Local database")
        elif "db:" in settings.database_url:
            print("🐳 Mode: Docker database")
        else:
            print("❓ Mode: Unknown")
            
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")


def main():
    if len(sys.argv) == 1:
        print("🔄 Database switching utility")
        print("\nAvailable commands:")
        print("  python switch_db.py local   - switch to local database")
        print("  python switch_db.py docker  - switch to Docker database")
        print("  python switch_db.py status  - show current configuration")
        print()
        show_current_config()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_current_config()
    elif command in ["local", "docker"]:
        switch_database(command)
    else:
        print(f"❌ Unknown command: {command}")
        print("Use: local, docker or status")


if __name__ == "__main__":
    main()
