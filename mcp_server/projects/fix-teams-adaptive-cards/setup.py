#!/usr/bin/env python3
"""
Setup script for Teams Adaptive Cards Fixer
"""
import os
import sys
from pathlib import Path

def main():
    """Setup the application"""
    print("🚀 Setting up Teams Adaptive Cards Fixer")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        
        # Copy from .env.example
        example_file = Path(".env.example")
        if example_file.exists():
            env_file.write_text(example_file.read_text())
            print("✅ .env file created!")
            print("")
            print("⚠️  IMPORTANT: Please edit .env file with your Azure AD app details:")
            print("   - CLIENT_ID: Your Azure AD app client ID")
            print("   - CLIENT_SECRET: Your Azure AD app client secret")
            print("   - TENANT_ID: Your Azure AD tenant ID")
            print("")
        else:
            print("❌ .env.example file not found!")
            return 1
    else:
        print("✅ .env file already exists")
    
    # Check if all required values are set
    print("🔧 Checking configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['CLIENT_ID', 'CLIENT_SECRET', 'TENANT_ID']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f'your_{var.lower()}_here':
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing configuration: {', '.join(missing_vars)}")
        print("")
        print("Please edit your .env file and set the following variables:")
        for var in missing_vars:
            print(f"   {var}=your_actual_value_here")
        print("")
        print("Then run this setup script again.")
        return 1
    
    print("✅ Configuration looks good!")
    print("")
    print("🎉 Setup complete! You can now run the application:")
    print("")
    print("   python main.py --colleagues \"John Smith,Jane Doe\" --update-type completed")
    print("")
    print("For help:")
    print("   python main.py --help")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
