#  This file is part of OctoBot Node (https://github.com/Drakkar-Software/OctoBot-Node)
#  Copyright (c) 2025 Drakkar-Software, All rights reserved.
#
#  OctoBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  OctoBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with OctoBot. If not, see <https://www.gnu.org/licenses/>.
import argparse
import sys

try:
    import uvicorn
except ImportError:
    print(
        "Error importing uvicorn, please install OctoBot-Node with all dependencies. "
        "Example: \"pip install -U octobot-node\" "
        "(Error: uvicorn not found)", file=sys.stderr
    )
    sys.exit(-1)

from octobot_node import PROJECT_NAME, LONG_VERSION


def start_server(args):
    host = args.host or "0.0.0.0"
    port = args.port or 8000
    workers = args.workers or 1
    reload = args.reload or False
    
    # Reload is only supported with a single worker
    if reload and workers > 1:
        print("Warning: --reload is only supported with a single worker. Ignoring --workers option.", file=sys.stderr)
        workers = 1
    
    # Import the app here to ensure settings are loaded
    from octobot_node.app.main import app
    
    # When using multiple workers, we need to pass the app as a string
    # When using a single worker, we can pass the app object directly for better reload support
    if workers > 1:
        # Use uvicorn with multiple workers
        uvicorn.run(
            "octobot_node.app.main:app",
            host=host,
            port=port,
            workers=workers,
        )
    else:
        # Single worker with reload support
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
        )


def octobot_node_parser(parser):
    """Configure argument parser for OctoBot-Node CLI."""
    parser.add_argument(
        '-v', '--version',
        help='Show OctoBot-Node current version.',
        action='store_true'
    )
    parser.add_argument(
        '--host',
        help='Host to bind the server to (default: 0.0.0.0).',
        type=str,
        default=None
    )
    parser.add_argument(
        '--port',
        help='Port to bind the server to (default: 8000).',
        type=int,
        default=None
    )
    parser.add_argument(
        '--workers',
        help='Number of worker processes (default: 1).',
        type=int,
        default=None
    )
    parser.add_argument(
        '--reload',
        help='Enable auto-reload for development (default: False).',
        action='store_true'
    )
    parser.set_defaults(func=start_octobot_node)


def start_octobot_node(args):
    if args.version:
        print(LONG_VERSION)
        return
    
    start_server(args)


def main(args=None):
    if not args:
        args = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        description=PROJECT_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    octobot_node_parser(parser)
    
    parsed_args = parser.parse_args(args)
    parsed_args.func(parsed_args)

