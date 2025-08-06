#!/usr/bin/env python3
"""
Quick fix script for Google Calendar authentication issues
"""

import os
import json

def fix_authentication():
    """
    Clean up authentication files and provide guidance
    """
    print("🔧 Google Calendar Authentication Fix")
    print("=" * 40)
    
    # Check for token.json and delete it
    if os.path.exists('token.json'):
        try:
            os.remove('token.json')
            print("✅ Deleted old token.json file")
        except Exception as e:
            print(f"❌ Could not delete token.json: {e}")
    else:
        print("ℹ️  No token.json file found")
    
    # Check for credentials.json
    if os.path.exists('credentials.json'):
        print("✅ Found credentials.json file")
        
        # Validate credentials file
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                if 'installed' in creds or 'web' in creds:
                    print("✅ Credentials file appears valid")
                else:
                    print("⚠️  Credentials file format may be incorrect")
        except Exception as e:
            print(f"⚠️  Could not validate credentials.json: {e}")
    else:
        print("❌ credentials.json file not found!")
        print("   Download it from Google Cloud Console")
    
    print("\n📋 Next Steps to Fix 'Access Blocked' Error:")
    print("1. Go to Google Cloud Console")
    print("2. Navigate to: APIs & Services > OAuth consent screen")
    print("3. Click on 'Test users' section")
    print("4. Add your email: tomerkeren42@gmail.com")
    print("5. Save changes")
    print("6. Run your calendar script again")
    
    print("\n🌐 Google Cloud Console link:")
    print("https://console.cloud.google.com/apis/credentials/consent")
    
    print("\n💡 If you have Google Workspace:")
    print("   Consider changing 'User Type' from 'External' to 'Internal'")
    print("   This allows all users in your organization to use the app")

if __name__ == "__main__":
    fix_authentication()