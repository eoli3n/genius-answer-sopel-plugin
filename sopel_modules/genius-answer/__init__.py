#! /usr/bin/env python3

import random
import re
import logging
import lyricsgenius
from sopel import plugin, tools

LOGGER = tools.get_logger('genius-answer')

def setup(bot):
    if "last_nick" not in bot.memory:
        bot.memory["last_nick"] = ""
    if "last_nick_count" not in bot.memory:
        bot.memory["last_nick_count"] = 0
    genius_token = bot.config.genius.api_key
    global genius
    genius = lyricsgenius.Genius(genius_token)
    genius.remove_section_headers = True
    genius.skip_non_songs = True

def get_words_in_text(text):
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
    hit=request['sections'][0]['hits'][0]
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

def search_next_line_by_song(sid, line):
    sanitized_line = re.sub(r"[^a-zA-ZÀ-ÿ ]+", "", line).lower().lstrip()
    text = genius.lyrics(song_id=sid)
    sanitized_text = re.sub(r"[^a-zA-ZÀ-ÿ ]+", "", text).lower()

    # speed up the process
    if sanitized_text.find(sanitized_line) != -1:
        text_list = text.split('\n')

        for row in text_list:
            nextsentence=False
            sanitized_row = re.sub(r"[^a-zA-ZÀ-ÿ ]+", "", row).lower().lstrip()

            # DEBUG
            #LOGGER.info(sanitized_line)
            #LOGGER.info(sanitized_row)

            # If input is the full sentence
            if sanitized_line == sanitized_row:
                nextsentence=True
            # If input is the begginning of a sentence, finish the sentence
            elif sanitized_line in sanitized_row:
                sanitized_line_list = sanitized_line.split(' ')
                last_line_word = sanitized_line_list[-1]
                current_index = text_list.index(row)
                current_sentence_list = text_list[current_index].split()

                # For all words that are not the last one of the sentence
                for word in current_sentence_list[:-1]:

                    sanitized_word = re.sub(r"[^a-zA-ZÀ-ÿ ]+", "", word).lower()
                    if sanitized_word == last_line_word:
                        next_word_index = current_sentence_list.index(word) + 1
                        end_line = " ".join(current_sentence_list[next_word_index:])
                        return end_line

                if current_sentence_list[-1]:
                    nextsentence=True

            # For the last word and full sentence
            if nextsentence:
                next_index = text_list.index(row) + 1
                next_line = text_list[next_index]
                return next_line

    return False

def genius_bot_answer(line):
    try:
        result = search_song_by_text(line)
        answer = search_next_line_by_song(result['song_id'], line)

        # if no text is returned, random answer
        if not answer:
            words = get_words_in_text(line)
            result = search_song_by_text(words)
            answer = search_line_by_song(result['song_id'])

        return answer

    except:
        return False

@plugin.rule(r'$nick (.*)')

def sentence_responder(bot, trigger):

    # configure fallback
    global fallback
    if bot.config.fallback.default:
        fallback = bot.config.fallback.default
    else:
        fallback = ""

    # limitation serial msg per nick
    if not trigger.sender.is_nick():
        if bot.memory["last_nick"] != trigger.nick:  
            bot.memory["last_nick"] = trigger.nick
            bot.memory["last_nick_count"] = 1
        else:
            bot.memory["last_nick_count"] += 1

        if getattr(bot.config.limitation, trigger.nick):
            if bot.memory["last_nick_count"] > int(getattr(bot.config.limitation, trigger.nick)):
                LOGGER.info(trigger.nick + " is now blocked")
                return

    message = trigger.group(1)
    response = genius_bot_answer(message)

    if not trigger.sender.is_nick():
        channel = bot.channels[trigger.sender].name.replace('#','')
        if getattr(bot.config.fallback, channel):
            fallback = getattr(bot.config.fallback, channel)
    # answer
    if response:
        bot.reply(response)
    # fallback msg
    elif fallback:
        bot.say(fallback)
