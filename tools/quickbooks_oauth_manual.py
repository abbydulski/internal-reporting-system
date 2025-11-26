"""
QuickBooks OAuth Setup - Manual Flow
For when you need to authorize on a different device.
"""

import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("QUICKBOOKS_CLIENT_ID")
CLIENT_SECRET = os.getenv("QUICKBOOKS_CLIENT_SECRET")

# Use a redirect URI that QuickBooks provides for development
REDIRECT_URI = "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"

# QuickBooks OAuth endpoints
AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


def get_authorization_url(use_production=False):
    """Generate the QuickBooks authorization URL."""
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'com.intuit.quickbooks.accounting',
        'state': 'manual_oauth_flow'
    }

    # Add parameter to skip sandbox requirement
    if use_production:
        params['environment'] = 'production'

    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_tokens(auth_code, realm_id):
    """Exchange the authorization code for access and refresh tokens."""
    print("\n3️⃣  Exchanging authorization code for tokens...")
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        response = requests.post(
            TOKEN_URL,
            headers=headers,
            data=data,
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        
        if response.status_code == 200:
            tokens = response.json()
            return tokens
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error exchanging code: {e}")
        return None


def main():
    """Main manual OAuth flow."""
    print("\n" + "="*80)
    print("  QUICKBOOKS OAUTH SETUP - MANUAL FLOW")
    print("="*80)
    
    # Check if we have client credentials
    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n❌ Missing QuickBooks credentials in .env file")
        print("\nPlease add to your .env file:")
        print("  QUICKBOOKS_CLIENT_ID=your_client_id")
        print("  QUICKBOOKS_CLIENT_SECRET=your_client_secret")
        return
    
    print(f"\n✅ Client ID found: {CLIENT_ID[:20]}...")
    print(f"✅ Client Secret found: {CLIENT_SECRET[:10]}...")
    
    print("\n" + "="*80)
    print("  MANUAL OAUTH FLOW")
    print("="*80)
    
    print("\n📝 INSTRUCTIONS:")
    print("\n1️⃣  First, add this redirect URI to your QuickBooks app:")
    print(f"   {REDIRECT_URI}")
    print("\n   Go to: https://developer.intuit.com/app/developer/myapps")
    print("   → Click your app → Keys & OAuth → Redirect URIs")
    print("   → Add the URI above and Save")
    
    input("\n   Press ENTER once you've added the redirect URI...")

    print("\n2️⃣  Choose authorization mode:")
    print("   [1] Sandbox (test data only)")
    print("   [2] Production (connect to real company)")
    mode = input("\n   Enter 1 or 2 [default: 2]: ").strip() or "2"

    use_production = (mode == "2")

    print("\n3️⃣  Copy this URL and open it in ANY browser (on any device):")
    print("\n" + "="*80)
    auth_url = get_authorization_url(use_production=use_production)
    print(auth_url)
    print("="*80)
    
    print("\n4️⃣  After you authorize:")
    print("   - You'll be redirected to a page showing the authorization code")
    print("   - The URL will look like:")
    print("   https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl?code=AB11...")
    print("   - Copy the ENTIRE URL from your browser")

    print("\n5️⃣  Paste the redirect URL here:")
    redirect_url = input("   Redirect URL: ").strip()
    
    # Parse the URL to extract code and realmId
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        
        if 'code' not in params:
            print("\n❌ No authorization code found in URL")
            print("   Make sure you copied the complete URL after authorizing")
            return
        
        auth_code = params['code'][0]
        realm_id = params.get('realmId', [None])[0]
        
        if not realm_id:
            print("\n⚠️  No Realm ID found in URL")
            realm_id = input("   Please enter your Company/Realm ID manually: ").strip()
        
        print(f"\n✅ Authorization code captured: {auth_code[:20]}...")
        print(f"✅ Realm ID: {realm_id}")
        
    except Exception as e:
        print(f"\n❌ Error parsing URL: {e}")
        print("\n   Let's try manually:")
        auth_code = input("   Enter the authorization code: ").strip()
        realm_id = input("   Enter the Realm ID (Company ID): ").strip()
    
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(auth_code, realm_id)
    
    if tokens:
        print("\n" + "="*80)
        print("  ✅ SUCCESS! YOUR CREDENTIALS:")
        print("="*80)
        
        print(f"\nRefresh Token: {tokens['refresh_token']}")
        print(f"Realm ID (Company ID): {realm_id}")
        print(f"Access Token (expires in {tokens['expires_in']} seconds): {tokens['access_token'][:50]}...")
        
        print("\n" + "="*80)
        print("  📝 UPDATE YOUR .ENV FILE")
        print("="*80)
        
        print("\nAdd these lines to your .env file:")
        print(f"\nQUICKBOOKS_REFRESH_TOKEN={tokens['refresh_token']}")
        print(f"QUICKBOOKS_REALM_ID={realm_id}")
        
        print("\n" + "="*80)
        print("  NEXT STEPS")
        print("="*80)
        
        print("\n1. Copy the lines above to your .env file")
        print("2. Update scheduler.py to use real QuickBooks extractor")
        print("3. Run: python -m etl.scheduler sync")
        
        print("\n✅ Setup complete!")
        
    else:
        print("\n❌ Failed to get tokens. Please try again.")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

