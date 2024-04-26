# sopel-genius-answer
A sopel plugin (irc-bot) to answer with a quote from rapgenius.com

### Install genius-answer plugin

```bash
$ pip install sopel_modules.genius-answer
```

### Configure genius-answer

To create the genius token, see https://github.com/johnwmillr/lyricsgenius#setup  
In ``default.cfg`` config file, add a ``[genius]`` section with ``api_key`` as

```ini
[genius]
api_key = xxxxxxxxxxxxxxxxx
```

### Configure per channel fallback answers
Bot will ``say``, not ``answer``.

```ini
[fallback]
default="I don't know dude."
channel="#channel is such a great place !"
```

### Per nickname serial answer limitation
To be able to limit how many answers to give to the same nickname.

```ini
[limitation]
pinpin=3
```
