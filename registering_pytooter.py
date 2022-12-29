#!/usr/bin/python3
# https://github.com/halcy/Mastodon.py

import pathlib
import sys
import argparse
from mastodon import Mastodon

scriptpath = pathlib.Path(__file__).parent.absolute()
clientcred = scriptpath.joinpath("pytooter_clientcred.secret")
usercred = scriptpath.joinpath("pytooter_usercred.secret")

parser = argparse.ArgumentParser()
parser.add_argument(
    "-u",
    "--user",
    required=True,
    help="Bot username (email address)",
)
parser.add_argument(
    "-i",
    "--instance",
    required=True,
    help="Fediverse instance (for @bot@masto.don it would be masto.don)",
)
parser.add_argument("-p", "--password", required=True, help="Bot password")
parser.add_argument(
    "-c",
    "--create_app",
    action="store_true",
    help="Create app, only needed for initial call",
)
args = parser.parse_args()
apiurl = "https://%s" % (args.instance)

# Register your app! This only needs to be done once (per server, or when
# distributing rather than hosting an application, most likely per device and server).
if args.create_app:
    Mastodon.create_app("herecomesthesun", api_base_url=apiurl, to_file=clientcred)

# Then, log in. This can be done every time your application starts (e.g. when writing a
# simple bot), or you can use the persisted information:
mastodon = Mastodon(client_id=clientcred, api_base_url=apiurl)

mastodon.log_in(
    username=args.user,
    password=args.password,
    to_file=usercred,
)

print(
    "If you see no error output, all is done. And you can run the regular bot script now"
)
