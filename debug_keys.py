#!/usr/bin/env python3
"""
Check what's actually in your .env file
"""
import os

def check_env_file():
    """Read and analyze .env file contents"""
    print("📂 CHECKING .env FILE CONTENTS")
    print("=" * 50)
    
    if not os.path.exists('.env'):
        print("❌ .env file does NOT exist!")
        print("💡 You need to create one with your Paystack credentials")
        return False
    
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        print(f"✅ .env file exists ({len(lines)} lines)")
        print("\n📋 File contents:")
        
        for i, line in enumerate(lines, 1):
            line = line.rstrip()
            if 'PAYSTACK' in line.upper():
                print(f"   {i:2d}: {line} {'⭐' if 'PAYSTACK' in line else ''}")
            else:
                print(f"   {i:2d}: {line}")
        
        # Look for specific keys
        paystack_lines = [line for line in lines if 'PAYSTACK' in line.upper()]
        
        print(f"\n🔍 PAYSTACK LINES FOUND: {len(paystack_lines)}")
        for line in paystack_lines:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                print(f"   {key}: {value[:20]}{'...' if len(value) > 20 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def check_environment_loading():
    """Test how python-dotenv loads the file"""
    print(f"\n🔄 TESTING ENVIRONMENT LOADING")
    print("=" * 30)
    
    try:
        from dotenv import load_dotenv
        
        # Load without any existing env vars
        result = load_dotenv(override=True)
        print(f"load_dotenv() result: {result}")
        
        # Check what got loaded
        secret = os.environ.get('PAYSTACK_SECRET_KEY')
        public = os.environ.get('PAYSTACK_PUBLIC_KEY')
        
        print(f"\nLoaded from environment:")
        print(f"   PAYSTACK_SECRET_KEY: {'✅ Found' if secret else '❌ Not found'}")
        if secret:
            print(f"      Length: {len(secret)}")
            print(f"      Value: {secret[:15]}...{secret[-10:]}")
            print(f"      Starts with sk_test_: {'✅ YES' if secret.startswith('sk_test_') else '❌ NO'}")
        
        print(f"   PAYSTACK_PUBLIC_KEY: {'✅ Found' if public else '❌ Not found'}")
        if public:
            print(f"      Length: {len(public)}")  
            print(f"      Value: {public[:15]}...{public[-10:]}")
            print(f"      Starts with pk_test_: {'✅ YES' if public.startswith('pk_test_') else '❌ NO'}")
    
    except Exception as e:
        print(f"❌ Error loading environment: {e}")

def show_correct_format():
    """Show what the .env file should look like"""
    print(f"\n✅ CORRECT .env FILE FORMAT:")
    print("=" * 30)
    
    correct_content = """# Development settings
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///blackshepherd.db

# Paystack Test Credentials (from your dashboard)
PAYSTACK_PUBLIC_KEY=pk_test_a65d73c793a4e431aac7def3cdea70a46c3323c
PAYSTACK_SECRET_KEY=sk_test_8feb610d84a6dc89ba3638663b7cfb501f90721
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret_here

# Site configuration
SITE_URL=http://localhost:5000
SITE_NAME=Black Shepherd Foundation"""
    
    print(correct_content)
    
    # Offer to create it
    print(f"\n💡 ACTIONS:")
    print("1. Copy the format above to your .env file")
    print("2. Or let me create a correct .env file for you")

if __name__ == '__main__':
    # Check current .env file
    env_exists = check_env_file()
    
    # Test environment loading
    check_environment_loading()
    
    # Show correct format
    show_correct_format()
    
    if env_exists:
        print(f"\n🔧 NEXT STEPS:")
        print("1. Check if your .env file matches the correct format above")
        print("2. Make sure there are no extra spaces around the = signs")
        print("3. Ensure the keys are exactly as shown (no missing characters)")
        print("4. Restart your terminal after making changes")
    else:
        print(f"\n🔧 NEXT STEPS:")
        print("1. Create a .env file in your project directory")
        print("2. Copy the correct format shown above")
        print("3. Run the test again")
    
    choice = input(f"\n❓ Would you like me to create/fix your .env file? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        try:
            correct_content = """# Development settings
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///blackshepherd.db

# Paystack Test Credentials (from your dashboard)
PAYSTACK_PUBLIC_KEY=pk_test_a65d73c793a4e431aac7def3cdea70a46c3323c
PAYSTACK_SECRET_KEY=sk_test_8feb610d84a6dc89ba3638663b7cfb501f90721
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret_here

# Site configuration
SITE_URL=http://localhost:5000
SITE_NAME=Black Shepherd Foundation"""
            
            with open('.env', 'w') as f:
                f.write(correct_content)
            
            print("✅ .env file created successfully!")
            print("🔄 Please restart your terminal and run: python test_paystack.py")
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            print("💡 Please create it manually using the format above")