import logging
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import parse_qs, urlparse

from src.mcp_kakao import kauth


class OauthListener(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/code":
            self.send_response(404)
            self.end_headers()
            return

        query = parse_qs(url.query)
        if "code" not in query:
            self.send_response(400)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write("Auth successful! You can close the tab!".encode("utf-8"))
        self.wfile.flush()

        storage = {}
        creds = kauth.get_credentials(authorization_code=query["code"][0], state=storage)

        t = threading.Thread(target=self.server.shutdown)
        t.daemon = True
        t.start()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-kakao")

def start_auth_flow(user_id: str):
    auth_url = kauth.get_authorization_url(state="")
    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        subprocess.Popen(['open', auth_url])
    else:
        import webbrowser
        webbrowser.open(auth_url)

    # start server for code callback
    server_address = ('', 8000)
    server = HTTPServer(server_address, OauthListener)
    server.serve_forever()

def setup_oauth2(user_id: str):
    # accounts = kauth.get_account_info()
    # if len(accounts) == 0:
    #     raise RuntimeError("No accounts specified in .gauth.json")
    # if user_id not in [a.email for a in accounts]:
    #     raise RuntimeError(f"Account for email: {user_id} not specified in .gauth.json")

    credentials = kauth.get_stored_credentials(user_id=user_id)
    if not credentials:
        start_auth_flow(user_id=user_id)
    else:
        if credentials.access_token_expired:
            logger.error("credentials expired. try refresh")

        # this call refreshes access token
        user_info = kauth.get_user_info(credentials=credentials)
        #logging.error(f"User info: {json.dumps(user_info)}")
        kauth.store_credentials(credentials=credentials, user_id=user_id)