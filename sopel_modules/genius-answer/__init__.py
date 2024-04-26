#! /usr/bin/env python3

import random
import re
import logging
import lyricsgenius
from sopel import plugin

logger = logging.getLogger(__name__)

def setup(bot):
    if "last_nick" not in bot.memory:
        bot.memory["last_nick"] = ""
    if "last_nick_count" not in bot.memory:
        bot.memory["last_nick_count"] = 0
    genius_token = bot.config.genius.api_key
    global genius
    genius = lyricsgenius.Genius(genius_token)
    genius.remove_section_headers = True
    global fallback
    if bot.config.fallback.default:
        fallback = bot.config.fallback.default
    else:
        fallback = ""

def get_two_words_in_text(text):
    splitted = text.split()
    for word in splitted:
        if not re.match("^[A-Za-zÀ-ÿ-']*$", word):
            splitted.remove(word)
    length = len(splitted)
    if length > 2:
        randomnum = random.randrange(length - 2)
        words = splitted[randomnum] + " " + splitted[randomnum + 1] 
    elif length == 2:
        words = splitted[0] + " " + splitted[1]
    elif length == 1:
        words = splitted [0]
    else:
        # TODO improve the noise here
        words = "salut"
    return words

def search_song_by_text(text):
    request = genius.search_lyrics(text)
    random_one_to_nine=random.randrange(10)
    hit=request['sections'][0]['hits'][random.randrange(10)]
    result = {
        "title": hit['result']['title'],
        "artist": hit['result']['artist_names'],
        "url": hit['result']['url'],
        "song_id": hit['result']['id']
    }
    return result

def search_line_by_song(sid):
    text = genius.lyrics(song_id=sid)
    text_list = text.split('\n')
    text_length = len(text_list) 
    randomnum = random.randrange(text_length - 1)
    line = text_list[randomnum]
    return line

def genius_bot_answer(line):
    try:
        words = get_two_words_in_text(line)
        result = search_song_by_text(words)
        answer = search_line_by_song(result['song_id'])
    except:
        return False
    return answer

@plugin.rule(r'(.*\b)($nickname)[ :,](.*)')

def sentence_responder(bot, trigger):

    # limitation serial msg per nick
    if bot.memory["last_nick"] != trigger.nick:  
        bot.memory["last_nick"] = trigger.nick
        bot.memory["last_nick_count"] = 1
    else:
        bot.memory["last_nick_count"] += 1

    if getattr(bot.config.limitation, trigger.nick):
        if bot.memory["last_nick_count"] > int(getattr(bot.config.limitation, trigger.nick)):
            logger.info(trigger.nick + " is now blocked")
            return

    message = trigger.group(1) + trigger.group(3)
    response = genius_bot_answer(message)

    channel = bot.channels[trigger.sender].name.replace('#','')
    if getattr(bot.config.fallback, channel):
        fallback = getattr(bot.config.fallback, channel)
    # answer
    if response:
        bot.reply(response)
    # fallback msg
    elif fallback:
        bot.say(fallback)
