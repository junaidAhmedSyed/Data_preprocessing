#!/usr/bin/env python3
"""
Setup script for Snowflake Table Statistics Dashboard
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def create_streamlit_directory():
    """Create .streamlit directory if it doesn't exist"""
    streamlit_dir = ".streamlit"
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
        print(f"📁 Created {streamlit_dir} directory")
    
    secrets_file = os.path.join(streamlit_dir, "secrets.toml")
    if not os.path.exists(secrets_file):
        print(f"📝 Please copy config_example.toml to {secrets_file} and fill in your Snowflake credentials")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Snowflake Table Statistics Dashboard...")
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create streamlit directory
    create_streamlit_directory()
    
    print("\n✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Copy config_example.toml to .streamlit/secrets.toml")
    print("2. Fill in your Snowflake credentials in secrets.toml")
    print("3. Run: streamlit run snowflake_stats_app.py")
    print("\n🎉 Happy analyzing!")

if __name__ == "__main__":
    main()