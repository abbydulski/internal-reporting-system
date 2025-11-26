"""
QuickBooks OAuth 2.0 Flow for PRODUCTION
Run this to get production access tokens.
"""

import os
import requests
from urllib.parse import urlencode
from etl.config import Config

def get_authorization_url():
    """Generate the OAuth authorization URL for PRODUCTION."""
    
    # PRODUCTION OAuth endpoint
    auth_url = "https://appcenter.intuit.com/connect/oauth2"
    
    params = {
        "client_id": Config.QUICKBOOKS_CLIENT_ID,
        "scope": "com.intuit.quickbooks.accounting",
        "redirect_uri": "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl",  # Use Intuit's playground
        "response_type": "code",
        "state": "production_setup"
    }
    
    url = f"{auth_url}?{urlencode(params)}"
    
    print("\n" + "="*70)
    print("QUICKBOOKS OAUTH SETUP - YOUR PRODUCTION DATA")
    print("="*70)
    print("\n📝 NOTE: Your app is in Development Mode, but you can still access")
    print("   YOUR OWN production QuickBooks company data!")
    print("   (No EULA/Privacy Policy needed for internal use)")
    print("\nStep 1: Visit this URL to authorize your PRODUCTION QuickBooks account:")
    print("\n" + url)
    print("\nStep 2: After authorizing, you'll be redirected to a URL like:")
    print("https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl?code=XXXXX&state=production_setup&realmId=XXXXX")
    print("\nStep 3: Copy the ENTIRE redirect URL and paste it below.")
    print("="*70 + "\n")
    
    return url

def exchange_code_for_tokens(auth_code: str, realm_id: str):
    """Exchange authorization code for access and refresh tokens."""
    
    token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"
    }
    
    # Use basic auth with client_id and client_secret
    auth = (Config.QUICKBOOKS_CLIENT_ID, Config.QUICKBOOKS_CLIENT_SECRET)
    
    print("\n🔄 Exchanging authorization code for tokens...")
    
    response = requests.post(token_url, headers=headers, data=data, auth=auth)
    
    if response.status_code == 200:
        tokens = response.json()
        
        print("\n" + "="*70)
        print("✅ SUCCESS! PRODUCTION DATA ACCESS OBTAINED")
        print("="*70)
        print("\nAdd these to your .env file:")
        print("\n# QuickBooks API (Your Production Company Data)")
        print(f"QUICKBOOKS_CLIENT_ID={Config.QUICKBOOKS_CLIENT_ID}")
        print(f"QUICKBOOKS_CLIENT_SECRET={Config.QUICKBOOKS_CLIENT_SECRET}")
        print(f"QUICKBOOKS_REFRESH_TOKEN={tokens['refresh_token']}")
        print(f"QUICKBOOKS_REALM_ID={realm_id}")
        print("\nNote: App is in Development Mode but accessing YOUR production data.")
        print("This is allowed without EULA/Privacy Policy for internal use!")
        print("\n" + "="*70 + "\n")
        
        return tokens
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None

def main():
    """Run the OAuth flow."""
    
    # Step 1: Get authorization URL
    auth_url = get_authorization_url()
    
    # Step 2: Wait for user to authorize and paste redirect URL
    redirect_url = input("\nPaste the full redirect URL here: ").strip()
    
    # Step 3: Parse the redirect URL
    if "code=" in redirect_url and "realmId=" in redirect_url:
        # Extract code and realmId from URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        
        auth_code = params.get("code", [None])[0]
        realm_id = params.get("realmId", [None])[0]
        
        if auth_code and realm_id:
            print(f"\n✓ Authorization Code: {auth_code[:20]}...")
            print(f"✓ Realm ID: {realm_id}")
            
            # Step 4: Exchange for tokens
            tokens = exchange_code_for_tokens(auth_code, realm_id)
            
            if tokens:
                print("\n🎉 You're all set! Update your .env file with the values above.")
                print("\nThen in etl/scheduler.py, make sure you have:")
                print("  is_sandbox=False  # Production mode")
        else:
            print("\n❌ Could not extract code or realmId from URL")
    else:
        print("\n❌ Invalid redirect URL. Make sure you copied the entire URL.")

if __name__ == "__main__":
    main()

