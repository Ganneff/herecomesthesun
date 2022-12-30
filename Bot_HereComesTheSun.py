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
from datetime import datetime, timedelta, time
from mastodon import Mastodon

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
args = parser.parse_args()

today = datetime.now()
yesterday = today - timedelta(days=1)
scriptpath = pathlib.Path(__file__).parent.absolute()
apikey = scriptpath.joinpath("API_key.txt")
mastodonsecret = scriptpath.joinpath("pytooter_usercred.secret")
cachefile = scriptpath.joinpath("cache.json")
localedir = scriptpath.joinpath("locales")

translate = gettext.translation("base", localedir=localedir, languages=[args.language])
translate.install()
_ = translate.gettext

if apikey.is_file():
    with open(apikey) as infile:
        # Read the key and use rstrip to ensure there is no linebreak or something left
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
sunrise_0 = datetime.fromisoformat(json_data["data"][0]["sunrise"])
sunrise_0 = sunrise_0 + timedelta(hours=1)
sunset_0 = datetime.fromisoformat(json_data["data"][0]["sunset"])
sunset_0 = sunset_0 + timedelta(hours=1)

day_1 = datetime.fromisoformat(json_data["data"][1]["time"])
sunrise_1 = datetime.fromisoformat(json_data["data"][1]["sunrise"])
sunrise_1 = sunrise_1 + timedelta(hours=1)
sunset_1 = datetime.fromisoformat(json_data["data"][1]["sunset"])
sunset_1 = sunset_1 + timedelta(hours=1)

delta_0 = sunset_0 - sunrise_0
delta_1 = sunset_1 - sunrise_1
diff = delta_1 - delta_0
diff2 = delta_0 - delta_1
if diff > diff2:
    direction = _("direction.more") + " "
    diff_total = time.fromisoformat("0" + str(diff))
else:
    direction = _("direction.less") + " "
    diff_total = time.fromisoformat("0" + str(diff2))

diff_sec = int(diff_total.strftime("%S"))
diff_min = int(diff_total.strftime("%M"))
diff_hour = int(diff_total.strftime("%H"))

and_sec = False
and_min = False
and_hour = False

if diff_sec == 0:
    diff_sec_str = ""
else:
    diff_sec_str = translate.ngettext("one.second", "%(num)d seconds", diff_sec) % {
        "num": diff_sec
    }
    and_sec = True

if diff_min == 0:
    diff_min_str = ""
else:
    diff_min_str = translate.ngettext("one.minute", "%(num)d minutes", diff_min) % {
        "num": diff_min
    }
    and_min = True

if diff_hour == 0:
    diff_hour_str = ""
else:
    diff_hour_str = translate.ngettext("one.hour", "%(num)d hours", diff_hour) % {
        "num": diff_hour
    }
    and_hour = True

if and_min is False and and_hour is False and and_sec is True:
    moreorless = """%s %s %s %s""" % (
        _("thats"),
        diff_sec_str,
        direction,
        _("thanyesterday"),
    )
elif and_sec is False and and_min is True and and_hour is False:
    moreorless = """%s %s %s %s""" % (
        _("thats"),
        diff_min_str,
        direction,
        _("thanyesterday"),
    )
elif and_sec is True and and_min is True and and_hour is False:
    moreorless = """%s %s %s %s %s %s""" % (
        _("thats"),
        diff_min_str,
        _("and"),
        diff_sec_str,
        direction,
        _("thanyesterday"),
    )
elif and_sec is False and and_min is False and and_hour is True:
    moreorless = """%s %s %s %s""" % (
        _("thats"),
        diff_hour_str,
        direction,
        _("thanyesterday"),
    )
elif and_sec is True and and_min is False and and_hour is True:
    moreorless = """%s %s %s %s %s %s""" % (
        _("thats"),
        diff_hour_str,
        _("and"),
        diff_sec_str,
        direction,
        _("thanyesterday"),
    )
elif and_sec is False and and_min is True and and_hour is True:
    moreorless = """%s %s %s %s %s %s""" % (
        _("thats"),
        diff_hour_str,
        _("and"),
        diff_min_str,
        direction,
        _("thanyesterday"),
    )
elif and_sec is True and and_min is True and and_hour is True:
    moreorless = """%s %s, %s %s %s %s %s """ % (
        _("thats"),
        diff_hour_str,
        diff_min_str,
        _("and"),
        diff_sec_str,
        direction,
        _("thanyesterday"),
    )
else:
    moreorless = _("exactly.same.as.yesterday")

toot = """%s %s %s %s:
%s %s %s %s.
%s %s

%s
    """ % (
    _("herecomessun"),
    args.city,
    _("on"),
    day_1.strftime("%a, %b %d"),
    _("sunrisesat"),
    sunrise_1.strftime("%H:%M"),
    _("sunsetsat"),
    sunset_1.strftime("%H:%M"),
    _("maximumdaylight"),
    str(delta_1),
    moreorless,
)

mastodon = Mastodon(access_token=mastodonsecret)
mastodon.status_post(toot)
