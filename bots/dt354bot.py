import socket
# from time import sleep

MSG = 'PRIVMSG'
JOIN = 'JOIN'
NICK = 'NICK'
USER = 'USER'

class Bot:
    def __init__(self, server, port, channel, nick_name):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
        self.sock = s.makefile()
        self.channel = channel

        self.send_msg(USER, msg='{nick_name} 0 * :{nick_name}'.format(
            nick_name=nick_name))
        self.send_msg(NICK, nick_name)
        self.think()

    def send_msg(self, category, channel='', msg=''):
        full_command = category + ' ' + channel + ' ' + msg
        print ">>>" + full_command
        self.sock.write(full_command + "\r\n")
        self.sock.flush()

    def think(self):
        while True: #MUHAHAHA
            # sleep(1)
            msg = self.sock.readline()
            if msg is "":
                continue
            msg = msg.rstrip()
            print ">>>", msg
            self.parse(msg)

    def parse(self, msg):
        msgSplit = msg.split(' ')
        if msgSplit[0] == 'PING':
            self.send_msg("PONG", msgSplit[1])

        elif msg[0] == ':':
            if msgSplit[1] == '001':
                self.send_msg(JOIN, channel=self.channel)
            elif msgSplit[1] == "PRIVMSG":
                print msgSplit
                chan = msgSplit[2]
                text = msgSplit[3][1:]
                if "tell me a joke" in text:
                    self.send_msg(MSG, channel=chan, msg=":I like beer! CHEERS!")
                if "haha" in text:
                    self.send_msg(MSG, channel=chan, msg=":Hahaha! That is FUNNY! I need to grab some popcorn!!!xD")
                if "rdy" in text:
                    self.send_msg(MSG, channel=chan, msg=":.ready up da!! Svette nerder har ikke hele dagen...:D")

if __name__ == '__main__':
    bot = Bot('irc.quakenet.org', 6667, '#dt354', 'jordansBotch')
