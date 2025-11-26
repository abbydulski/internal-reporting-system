"""
QuickBooks OAuth Setup Tool
Helps you get your Refresh Token and Realm ID using your Client ID and Client Secret.
"""

import os
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from dotenv import load_dotenv
import http.server
import socketserver
from threading import Thread
import time

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("QUICKBOOKS_CLIENT_ID")
CLIENT_SECRET = os.getenv("QUICKBOOKS_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"

# QuickBooks OAuth endpoints
AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

# Global variable to store the authorization code
auth_code = None
realm_id = None


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handle the OAuth callback from QuickBooks."""
    
    def do_GET(self):
        global auth_code, realm_id
        
        # Parse the callback URL
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            realm_id = params.get('realmId', [None])[0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <html>
            <head><title>QuickBooks OAuth Success</title></head>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1 style="color: green;">✅ Authorization Successful!</h1>
                <p>You can close this window and return to your terminal.</p>
                <p>The authorization code has been captured.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = """
            <html>
            <head><title>QuickBooks OAuth Error</title></head>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1 style="color: red;">❌ Authorization Failed</h1>
                <p>No authorization code received.</p>
                <p>Please try again.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        # Suppress server logs
        pass


def start_callback_server():
    """Start a local server to receive the OAuth callback."""
    PORT = 8000
    
    with socketserver.TCPServer(("", PORT), OAuthCallbackHandler) as httpd:
        print(f"   Callback server started on port {PORT}")
        print(f"   Waiting for authorization...\n")
        
        # Run until we get the auth code
        while auth_code is None:
            httpd.handle_request()
        
        print(f"   ✅ Authorization code received!")


def get_authorization_url():
    """Generate the QuickBooks authorization URL."""
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'com.intuit.quickbooks.accounting',
        'state': 'security_token_' + str(int(time.time()))
    }
    
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_tokens(auth_code):
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
    """Main OAuth flow."""
    print("\n" + "="*80)
    print("  QUICKBOOKS OAUTH SETUP")
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
    print("  OAUTH FLOW")
    print("="*80)
    
    print("\n1️⃣  Starting local callback server...")
    
    # Start the callback server in a separate thread
    server_thread = Thread(target=start_callback_server, daemon=True)
    server_thread.start()
    
    time.sleep(1)  # Give server time to start
    
    print("\n2️⃣  Opening QuickBooks authorization page in your browser...")
    print("\n   📝 INSTRUCTIONS:")
    print("   1. A browser window will open")
    print("   2. Sign in to your QuickBooks account")
    print("   3. Select the company you want to connect")
    print("   4. Click 'Authorize' to grant access")
    print("   5. You'll be redirected back automatically")
    
    auth_url = get_authorization_url()
    
    print(f"\n   If the browser doesn't open, visit this URL:")
    print(f"   {auth_url}\n")
    
    input("   Press ENTER to open the browser...")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Wait for the callback
    while auth_code is None:
        time.sleep(1)
    
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(auth_code)
    
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
        print("2. Switch back to the real QuickBooks extractor in scheduler.py:")
        print("   from etl.extractors.quickbooks_extractor import QuickBooksExtractor")
        print("3. Run: python -m etl.scheduler sync")
        
        print("\n✅ Setup complete!")
        
    else:
        print("\n❌ Failed to get tokens. Please try again.")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

