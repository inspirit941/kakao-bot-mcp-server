import json
import logging
import subprocess
import sys
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent, ImageContent, EmbeddedResource
from typing_extensions import Any, Sequence

from mcp_kakao import toolhandler
from mcp_kakao import kauth, tools_message


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
        creds = kauth.get_credentials(authorization_code=query["code"][0], state="")

        t = threading.Thread(target=self.server.shutdown)
        t.daemon = True
        t.start()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-kakao")


def start_auth_flow(email_address: str, state: str):
    auth_url = kauth.get_authorization_url(email_address, state=state)
    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        subprocess.Popen(["open", auth_url])
    else:
        import webbrowser
        webbrowser.open(auth_url)

    # start server for code callback
    server_address = ("", 8000)
    server = HTTPServer(server_address, OauthListener)
    server.serve_forever()


def setup_oauth2(email_address: str):
    accounts = kauth.get_account_info()
    if len(accounts) == 0:
        raise RuntimeError("No accounts specified in .accounts.json")
    if email_address not in [a.email for a in accounts]:
        raise RuntimeError(
            f"Account for email: {email_address} not specified in .accounts.json"
        )

    credentials = kauth.get_stored_credentials(email_address=email_address)
    if not credentials:
        start_auth_flow(email_address=email_address, state="")
    else:
        if credentials.access_token_expired:
            logger.error("credentials expired. try refresh")

        # this call refreshes access token
        user_info = kauth.get_user_info(credentials=credentials)
        logging.error(f"User info: {json.dumps(user_info)}")
        kauth.store_credentials(credentials=credentials, email_address=email_address)


app = Server("mcp-kakao")

tool_handlers = {}


def add_tool_handler(tool_class: toolhandler.ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class


def get_tool_handler(name: str) -> toolhandler.ToolHandler | None:
    if name not in tool_handlers:
        return None

    return tool_handlers[name]


add_tool_handler(tools_message.SendCalendarTemplateToMeToolHandler())
add_tool_handler(tools_message.SendCommerceTemplateToMeToolHandler())
add_tool_handler(tools_message.SendLocationTemplateToMeToolHandler())
add_tool_handler(tools_message.SendFeedTemplateToMeToolHandler())
add_tool_handler(tools_message.SendListTemplateToMeToolHandler())
add_tool_handler(tools_message.SendTextTemplateToMeToolHandler())


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [th.get_tool_description() for th in tool_handlers.values()]


@app.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    try:
        if not isinstance(arguments, dict):
            raise RuntimeError("arguments must be dictionary")

        if toolhandler.EMAIL_ADDRESS_ARG not in arguments:
            raise RuntimeError("email_address argument is missing in dictionary.")

        setup_oauth2(email_address=arguments.get(toolhandler.EMAIL_ADDRESS_ARG, ""))

        tool_handler = get_tool_handler(name)
        if not tool_handler:
            raise ValueError(f"Unknown tool: {name}")

        return tool_handler.run_tool(arguments)
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error(f"Error during call_tool: str(e)")
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")


async def main():
    print(sys.platform)
    accounts = kauth.get_account_info()
    for account in accounts:
        creds = kauth.get_stored_credentials(email_address=account.email)
        if creds:
            logging.info(f"found credentials for {account.email}")

    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
