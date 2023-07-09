#!/usr/bin/python3
# coding: utf-8
"""
author: Henrik Schönemann, Joerg Jaspert
created on: 2022-12-29
coding: utf-8

https://github.com/halcy/Mastodon.py
https://docs.stormglass.io/#/

Copyright (C) 2022 Henrik Schönemann
Copyright (C) 2022 by Joerg Jaspert <joerg@ganneff.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

import requests
import pathlib
import sys
import json
import argparse
import gettext
import i18n
from datetime import datetime, timedelta, time
from mastodon import Mastodon
from babel.dates import format_date, format_timedelta
import humanize
from jinja2 import FileSystemLoader, Environment

# Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument(
    "-l",
    "--lat",
    default="50.549672",
    help="Latitude",
)
parser.add_argument(
    "-o",
    "--long",
    default="9.668899",
    help="Longitude",
)
parser.add_argument(
    "-c",
    "--city",
    default="Fulda",
    help="Location name",
)
parser.add_argument(
    "-t",
    "--language",
    default="en",
    help="Language of the text output",
)
parser.add_argument(
    "-p",
    "--postat",
    default="direct",
    choices=["direct", "time", "sunset", "sunrise"],
    help="When to post? Direct, scheduled for a set time or scheduled for either sunset or sunrise?",
)
parser.add_argument(
    "-z",
    "--time",
    default="06:01",
    help="When to post? Just the time string, ie. 06:01 for one minute after six 'o clock. Mastodon wants this to be at least 5 minutes into the future.",
)
args = parser.parse_args()

today = datetime.now()
yesterday = today - timedelta(days=1)
scriptpath = pathlib.Path(__file__).parent.absolute()
apikey = scriptpath.joinpath("API_key.txt")
mastodonsecret = scriptpath.joinpath("pytooter_usercred.secret")
cachefile = scriptpath.joinpath("cache.json")
localedir = scriptpath.joinpath("locales")

# Want to translate some strings
translate = gettext.translation("base", localedir=localedir, languages=[args.language])
translate.install()
_ = translate.gettext

# Jinja2 Templating
loader = FileSystemLoader(searchpath=scriptpath)
env = Environment(loader=loader, extensions=["jinja2.ext.i18n"])
templates = {}
templates["toot"] = env.get_template("toot.tmpl")
templates["diff"] = env.get_template("diff.tmpl")
i18n.setLocale(args.language)
env.install_gettext_translations(i18n)

# humanize supports zh_CN but not zh_TW. Fallback.
if args.language == "zh_TW":
    _t = humanize.i18n.activate("zh_CN")
else:
    # en is the default for humanize, so nothing to activate
    if args.language != "en":
        _t = humanize.i18n.activate(args.language)

if apikey.is_file():
    with open(apikey) as infile:
        # Read the key and use rstrip to ensure there is no linebreak
        # or something left
        key = infile.readlines()[0].rstrip()
else:
    print(_("needapikey") + " %s" % (scriptpath))
    sys.exit(1)

if not mastodonsecret.is_file():
    print(_("nousersecret"))
    sys.exit(2)

if cachefile.is_file():
    mtime = cachefile.stat().st_mtime
    epoch = datetime.now().timestamp()
    diff = epoch - mtime
else:
    # No cachefile, use large diff, so we will request data from http
    diff = 42424242

if diff > 60 * 60 * 6:
    # Cachefile is old or does not exist, ask api again
    response = requests.get(
        "https://api.stormglass.io/v2/astronomy/point",
        params={
            "lat": args.lat,
            "lng": args.long,
            "start": yesterday,
            "end": today,
        },
        headers={"Authorization": key},
    )
    json_data = response.json()
    with open(cachefile, "w") as outfile:
        json.dump(json_data, outfile)
else:
    # Cachefile is recent, use it
    with open(cachefile) as infile:
        json_data = json.load(infile)

day_0 = datetime.fromisoformat(json_data["data"][0]["time"])
sunrise_0 = datetime.fromisoformat(json_data["data"][0]["sunrise"]).astimezone()
sunset_0 = datetime.fromisoformat(json_data["data"][0]["sunset"]).astimezone()

day_1 = datetime.fromisoformat(json_data["data"][1]["time"])
sunrise_1 = datetime.fromisoformat(json_data["data"][1]["sunrise"]).astimezone()
sunset_1 = datetime.fromisoformat(json_data["data"][1]["sunset"]).astimezone()

delta_0 = sunset_0 - sunrise_0
delta_1 = sunset_1 - sunrise_1
diff = delta_1 - delta_0
diff2 = delta_0 - delta_1
if diff > diff2:
    # transcomment Word(s) used if more suntime is available than
    # yesterday. English more. Will be used in later translation to
    # combine with actual time difference-
    direction = _("direction.more") + " "
    diff_total = time.fromisoformat("0" + str(diff))
    hashtag = _("hashtag.itcomes")
else:
    # transcomment Word(s) used if less suntime is available than
    # yesterday. English less. Will be used in later translation to
    # combine with actual time difference-
    direction = _("direction.less") + " "
    diff_total = time.fromisoformat("0" + str(diff2))
    hashtag = _("hashtag.itgoes")

# Create the Text on how many hours/minutes/seconds difference there are to yesterday
difftext = templates["diff"].render(
    hours=format_timedelta(
        timedelta(hours=int(diff_total.strftime("%H"))),
        granularity="hours",
        locale=args.language,
    ),
    minutes=format_timedelta(
        timedelta(minutes=int(diff_total.strftime("%M"))),
        granularity="minutes",
        locale=args.language,
    ),
    seconds=format_timedelta(
        timedelta(seconds=int(diff_total.strftime("%S"))),
        granularity="seconds",
        threshold=1.5,
        locale=args.language,
    ),
    moreorless=direction,
)

toot = templates["toot"].render(
    hashtag=hashtag,
    city=args.city,
    date=format_date(day_1, format="full", locale=args.language),
    sunrisetime=sunrise_1.strftime("%H:%M"),
    sunsettime=sunset_1.strftime("%H:%M"),
    difftime=difftext,
    maximumtime=humanize.precisedelta(delta_1),
)

mastodon = Mastodon(access_token=mastodonsecret)

# We may be asked to post at a different time than now
if args.postat == "sunset":
    posttime = sunset_1
elif args.postat == "sunrise":
    posttime = sunrise_1
else:
    posttime = datetime.combine(datetime.today(), time.fromisoformat(args.time))

# Mastodon wants scheduled posts at least 5 minutes in the future. So
# we can't do "NOW" posts with a schedule attached.
if args.postat == "direct":
    mastodon.status_post(toot, language=args.language)
else:
    reply = mastodon.status_post(toot, language=args.language, scheduled_at=posttime)
