"""
QuickBooks OAuth Setup Helper
==============================
This script helps you get your initial refresh token for QuickBooks API.

Run this ONCE to get your refresh token, then save it to your .env file.
"""

import requests
import webbrowser
from urllib.parse import urlencode, parse_qs
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# You'll fill these in from your QuickBooks app
CLIENT_ID = "ABAwCsLtPNZpjA7YLAmiM7rhfvqZbAkCQbsSt1ZB3KbrMLs4Jx"  # From Keys & Credentials page
CLIENT_SECRET = "Rr83ODZCMutu5VxzP7IWvgcDIZj0J1owq07vXDch"  # From Keys & Credentials page

# OAuth settings
REDIRECT_URI = "http://localhost:8000/callback"
SCOPE = "com.intuit.quickbooks.accounting"
AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

# Storage for the authorization code
auth_code = None
realm_id = None


class CallbackHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback from QuickBooks."""
    
    def do_GET(self):
        global auth_code, realm_id
        
        # Parse the callback URL
        query = self.path.split('?')[1] if '?' in self.path else ''
        params = parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            realm_id = params.get('realmId', [None])[0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            success_html = """
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: green;">Success!</h1>
                    <p>Authorization complete. You can close this window and return to your terminal.</p>
                </body>
                </html>
            """
            self.wfile.write(success_html.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = """
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Error</h1>
                    <p>Authorization failed. Please try again.</p>
                </body>
                </html>
            """
            self.wfile.write(error_html.encode('utf-8'))
    
    def log_message(self, format, *args):
        # Suppress server logs
        pass


def start_local_server():
    """Start a local server to receive the OAuth callback."""
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    return server, thread


def get_authorization_url():
    """Generate the QuickBooks authorization URL."""
    params = {
        'client_id': CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'state': 'test123'
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_tokens(auth_code):
    """Exchange authorization code for access and refresh tokens."""
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data=data,
        headers={'Accept': 'application/json'}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error exchanging code: {response.status_code}")
        print(response.text)
        return None


def main():
    """Main OAuth flow."""
    print("\n" + "="*70)
    print("QUICKBOOKS OAUTH SETUP")
    print("="*70 + "\n")
    
    # Check if credentials are set
    if CLIENT_ID == "YOUR_CLIENT_ID_HERE" or CLIENT_SECRET == "YOUR_CLIENT_SECRET_HERE":
        print("ERROR: You need to set your CLIENT_ID and CLIENT_SECRET first!")
        print("\nSteps:")
        print("1. Go to developer.intuit.com")
        print("2. Open your app -> Keys & Credentials")
        print("3. Copy Client ID and Client Secret (Development mode)")
        print("4. Edit this file and replace the values at the top")
        print("5. Run this script again")
        return
    
    print("Setup Instructions:")
    print("\n1. Make sure you have:")
    print("   - Created a sandbox company in QuickBooks")
    print("   - Added http://localhost:8000/callback to your app's redirect URIs")
    print("\n2. To add redirect URI:")
    print("   a. Go to developer.intuit.com -> Your App -> Keys & Credentials")
    print("   b. Scroll to 'Redirect URIs'")
    print("   c. Add: http://localhost:8000/callback")
    print("   d. Click 'Save'")
    
    input("\nPress Enter when ready to continue...")
    
    # Start local callback server
    print("\nStarting local server on http://localhost:8000...")
    server, thread = start_local_server()
    
    # Generate authorization URL
    auth_url = get_authorization_url()
    
    print("\nOpening browser for authorization...")
    print(f"If browser doesn't open, visit: {auth_url}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Wait for callback
    print("Waiting for authorization (sign in and click 'Connect')...")
    thread.join(timeout=300)  # 5 minute timeout
    
    if not auth_code:
        print("\nAuthorization timed out or failed.")
        print("Please try again.")
        return
    
    print(f"\nAuthorization code received!")
    print(f"Realm ID (Company ID): {realm_id}")
    
    # Exchange code for tokens
    print("\nExchanging code for tokens...")
    tokens = exchange_code_for_tokens(auth_code)
    
    if tokens:
        print("\n" + "="*70)
        print("SUCCESS! Save these to your .env file:")
        print("="*70)
        print(f"\nQUICKBOOKS_CLIENT_ID={CLIENT_ID}")
        print(f"QUICKBOOKS_CLIENT_SECRET={CLIENT_SECRET}")
        print(f"QUICKBOOKS_REFRESH_TOKEN={tokens['refresh_token']}")
        print(f"QUICKBOOKS_REALM_ID={realm_id}")
        print(f"\n# Access token (expires in 1 hour, will auto-refresh):")
        print(f"# {tokens['access_token'][:50]}...")
        print("\n" + "="*70)
        
        # Save to file for convenience
        with open('quickbooks_tokens.txt', 'w') as f:
            f.write(f"QUICKBOOKS_CLIENT_ID={CLIENT_ID}\n")
            f.write(f"QUICKBOOKS_CLIENT_SECRET={CLIENT_SECRET}\n")
            f.write(f"QUICKBOOKS_REFRESH_TOKEN={tokens['refresh_token']}\n")
            f.write(f"QUICKBOOKS_REALM_ID={realm_id}\n")
        
        print("\nAlso saved to 'quickbooks_tokens.txt' for your reference")
        print("\nNext steps:")
        print("1. Copy the values above to your .env file")
        print("2. Use the real QuickBooks extractor (coming next!)")
        
    else:
        print("\nFailed to get tokens. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\nError: {e}")