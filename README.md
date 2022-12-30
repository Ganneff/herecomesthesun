# Here Comes The Sun

A tiny Fediverse bot posting sunruse, sunset, amount of daylight and
the difference in daylight to the day before.

The bot in action: <a rel="me" href="https://fulda.social/@herecomesthesun">Here Comes The Sun Fulda</a>

It is based on (basically an extended version of) the bot
[SunofBerlin](https://github.com/Schoeneh/snippets/tree/main/Mastodon_bots/%40sunofberlin)
from [Henrik Schoenemann](https://mastodon.lol/@lavaeolus).

## Extras
* Reworked helper script to register an app with the Mastodon instance
  used. Check `registering_pytooter.py -h`
* Commandline support for the bot too, the Latitude, Longitude and
  Location name as well as language to use for the toot can be set
  without code changes.
* Uses caching, to not run over the limit of the stormglasss.io API
  (only real interesting if one runs it more than once a day)
* Translatable, using gettext. Check
  [Weblate](https://translate.codeberg.org/projects/here-comes-the-sun-fediverse-bot/)
  if you want to help translate.

## Usage
* Create a bot account on the instance you want to use. (Ensure the
  admins like bots!)
* Git clone the bots repository, cd into the new directory.
* Create an account on [Stormglass](https://stormglass.io/), the bot
  uses that API to get data. Get the API key and put it into
  API_KEY.txt in the bots directory.
* Run `./registering_pytooter.py -u emailofthebot@example.com -i
  instance.url -p botpassword -c` (note that instance.url is just the
  domain of the instance, without https://)
* Now you can run the bot, supplying the right values for its
  parameters. For example, to run it and show information for the
  middle of Fulda in German, run `./Bot_HereComesTheSun.py -l
  50.549672 -o 9.668899 -c Fulda -t de`
* Now you can cron this line to run once a day, e.g. use `crontab -e`
  and put the following in (adjust the path), to have it run in the
  morning at 06:01: `* 1 6 * * *
  $HOME/herecomesthesun/Bot_HereComesTheSun.py -l 50.549672 -o
  9.668899 -c Fulda -t de`
