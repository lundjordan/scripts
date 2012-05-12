import socket, urllib
from random import randint
from datetime import datetime
import botdata

MSG = 'PRIVMSG'
JOIN = 'JOIN'
NICK = 'NICK'
USER = 'USER {nick_name} 0 *'

JOKES = botdata.jokes_array
INSULTS = botdata.insults_array
CONFUSED = botdata.confused_array
GREETINGS = botdata.greetings_array
PEOPLE = botdata.people_dict

def getting_pinged(msg):
    """checks to see if server is pinging me"""
    if msg[0] == 'PING':
        return True
    else:
        return False

def get_date_info():
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday']
    today = datetime.now()

    return {
            'weekday' : weekdays[today.isoweekday()], 'month_day' : today.day,
            'month' : today.month, 'hour' : today.hour, 'min' : today.minute
            }

def _parse_weather_info(data, index):
    start_index = data.index(index) + len(index)
    stop_index = data.find(' ', start_index)
    return data[start_index:stop_index]

def get_weather():

    # http://www.worldweatheronline.com/Vancouver-weather/British-Columbia/CA.aspx
    # http://www.worldweatheronline.com/San-Francisco-weather/California/US.aspx

    weather_desc_index = '<div class="weatherdesc">'
    weather_temp_index = '<div class="temp">'

    url_tor = 'http://www.worldweatheronline.com/Toronto-weather/Ontario/CA.aspx'
    url_dub = 'http://www.worldweatheronline.com/Dublin-weather/Dublin/IE.aspx'
    data_dub = urllib.urlopen(url_dub).read()
    data_tor = urllib.urlopen(url_tor).read()

    tor_temp = _parse_weather_info(data_tor, weather_temp_index)
    tor_desc = _parse_weather_info(data_tor, weather_desc_index)
    dub_temp = _parse_weather_info(data_dub, weather_temp_index)
    dub_desc = _parse_weather_info(data_dub, weather_desc_index)

    today_info = get_date_info()
    weather_style = "For {weekday}, {month}/{day}, Toronto currently has a temp of {temp} \
            and is describes as {desc}"

    tor_final = weather_style.format(weekday=today_info['weekday'],
                        month=today_info['day'], day=today_info['month_day'],
                        temp=tor_temp, desc=tor_desc)
    dub_final = weather_style.format(weekday=today_info['weekday'],
                        month=today_info['day'], day=today_info['month_day'],
                        temp=dub_temp, desc=dub_desc)
    return (tor_final, dub_final)

class Bot:
    def __init__(self, server, port, channel, nick_name):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
        self.sock = s.makefile()
        self.channel = channel

        self.joke_answer = None

        user = USER.format(nick_name=nick_name)
        self.send_msg(user, msg=nick_name)
        self.send_msg(NICK, nick_name)
        self.nick_name = nick_name
        self.think()

    ###### Response Methods #########
    def tell_joke(self):
        response = JOKES[randint(0, len(JOKES)-1)]

        if len(response) > 1: # its a question joke
            self.joke_answer = response[1]
        self.send_msg(MSG, channel=self.channel, msg=response[0])

    def insult_someone(self, text):
        insultee_index = text.find('insult')+7
        insultee_name = text[insultee_index:]
        response = insultee_name + ', ' + INSULTS[randint(0, len(INSULTS)-1)]

        self.send_msg(MSG, channel=self.channel, msg=response)

    def check_if_joke_answer_correct(self, text):
        if self.joke_answer in text:
            response = 'Way to ruin the joke genius'
            self.joke_answer = None
        elif 't know' in text or 'what' in text or 'tell me' in text:
            response = self.joke_answer
            self.joke_answer = None
        else:
            response = "That's not the answer I was looking for. Guess again..."
        self.send_msg(MSG, channel=self.channel, msg=response)


    def tell_time(self):
        """give me the current time info"""
        today_info = get_date_info()
        tor_hour = today_info['hour']

        # should have used something from library :)
        if tor_hour + 5 > 24:
            dub_hour = tor_hour + 5 - 24
        else:
            dub_hour = tor_hour + 5

        date_style = "It is currently {hour}:{minute} on {weekday}, {month}/{day} in Toronto. \
                In Dublin it is {dub_hour}:{minute} or 5 hours ahead."
        response = date_style.format(weekday=today_info['weekday'],
                        month=today_info['day'], day=today_info['month_day'],
                        hour=tor_hour, minute=today_info['minute'],
                        dub_hour=dub_hour)
        self.send_msg(MSG, channel=self.channel, msg=response)

    def tell_weather(self):
        self.send_msg(MSG, channel=self.channel, msg='hmm, let me see...')
        tor_weather_msg, dub_weather_msg = get_weather()
        self.send_msg(MSG, channel=self.channel, msg=tor_weather_msg)
        self.send_msg(MSG, channel=self.channel, msg=dub_weather_msg)

    def tell_how_long_you_took(self):
        response = 'It took Jordan 3 beers and one lonely day to create me'
        self.send_msg(MSG, channel=self.channel, msg=response)

    def tell_best_language(self):
        response = "The best language all around (sys admin, network manager, web developer, \
                scripting, math, string manipulation, reg expressions, or anyone who is learning) \
                is easily python. Obviously..."
        self.send_msg(MSG, channel=self.channel, msg=response)

    def is_it_beer_time(self):
        current_weekday = get_date_info()['weekday']
        current_hour = get_date_info()['hour']

        if current_weekday in ['friday', 'Saturday', 'Sunday']:
            if current_hour > 17:
                response = "Sure its after 5 pm on a weekend(Toronto). Get locked!"
            else:
                response = "Well it is the weekend but not quite 5pm(Toronto). Who am I kidding, go for it!"
        else:
            if current_hour > 17:
                response = "Dude, its a weekday. At least it is after 5pm in Toronto. I won't judge you"
            else:
                response = "Man, its not even after 5pm in Toronto let alone the fact its a weekday. Pull yourself together"

        self.send_msg(MSG, channel=self.channel, msg=response)

    def say_hello(self, sender):
        response = GREETINGS[randint(0, len(GREETINGS)-1)].format(nick=sender)
        self.send_msg(MSG, channel=self.channel, msg=response)

    def say_who_is(self, text):
        name_start = text.find('who is') + 7
        name = text[name_start:].lower()
        if name in PEOPLE.keys():
            response = PEOPLE[name]
        else:
            response = "I don't know who you are talking about..."
        self.send_msg(MSG, channel=self.channel, msg=response)

    def say_what(self):
        response = CONFUSED[randint(0, len(CONFUSED)-1)]
        self.send_msg(MSG, channel=self.channel, msg=response)

    #################################

    def send_msg(self, category, channel='', msg=''):
        if msg:
            msg = ':' + msg
        full_command = category + ' ' + channel + ' ' + msg
        print ">>>" + full_command
        self.sock.write(full_command + "\r\n")
        self.sock.flush()

    def scan_message(self, msg):
        msg = msg.split(' ')

        if getting_pinged(msg):
            self.send_msg("PONG", msg[1])
        elif msg[0].startswith(':'):
            if msg[1] == '001':
                self.send_msg(JOIN, channel=self.channel)
            elif msg[1] == MSG:
                print msg
                text = ' '.join(msg[3:]).lower()
                sender = msg[0][:msg[0].find('!')]

                if text.find(self.nick_name) >= 0:
                    self._find_response(sender, text)
                else:
                    pass # ignore

    def _find_response(self, sender, text):
        # ugly else if block
        if self.joke_answer: # waiting on a joke answer
            self.check_if_joke_answer_correct(text)
        elif self.nick_name and 'joke' in text:
            self.tell_joke()
        elif 'insult' in text and text.endswith('insult') != True:
            self.insult_someone(text)
        elif 'is the time' in text or 'time is it' in text:
            self.tell_time()
        elif 'how long' in text and 'jlund' in text and 'program' in text:
            self.tell_how_long_you_took()
        elif 'is' in text and 'best' in text and 'language' in text:
            self.tell_best_language()
        elif 'beer' in text:
            self.is_it_beer_time()
        elif 'temperature' in text or 'weather' in text:
            self.is_it_beer_time()
        elif 'hello' in text or 'hi ' in text:
            self.say_hello(sender)
        elif 'who is' in text:
            self.say_who_is(text)
        else:
            self.say_what()

    ### RUN
    def think(self):
        while True: #MUHAHAHA
            # sleep(1)
            msg = self.sock.readline()
            if msg is "":
                continue
            msg = msg.rstrip()
            print ">>>", msg
            self.scan_message(msg)


#!/usr/bin/python

import optparse

parser = optparse.OptionParser()
parser.add_option('-n', '--new', help='creates a new object')

(opts, args) = parser.parse_args()
if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('-s', '--server', action='store', dest='serv',
            help='Mandatory. Specify the server eg: irc.quakenet.org')
    parser.add_option('-n', '--port', action='store', dest='port',
            help='Mandatory. Specify the port eg: 6667')
    parser.add_option('-c', '--channel', action='store', dest='chan',
        help='Mandatory. Specify the channel eg: #dt354')
    parser.add_option('-n', '--nick', action='store', dest='ni',
            help='Mandatory. Specify the nickname')

    mandatory_list = ['serv', 'port', 'chan', 'ni']
    (opts, args) = parser.parse_args()

    for o in mandatory_list:
        if not opts.__dict__[0]:
            print "mandatory option is missing\n"
            parser.print_help()
            exit(-1)

    # bot = Bot('irc.quakenet.org', 6667, '#dt354', 'jordans_slave')
    bot = Bot(opts.serv, opts.port, opts.chan, opts.ni)
