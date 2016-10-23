import logging
import string
import time
import _thread

import irc
import irc.client

import galax.util
import galax.channels.channel

logger = logging.getLogger(__name__)


IRC_SERVER = "chat.freenode.net"
IRC_PORT = 6667


class IrcChannel(galax.channels.channel.Channel):
    def __init__(self, server, recv_callback):
        super(IrcChannel, self).__init__(server, recv_callback)

        logging.getLogger("irc").setLevel(logging.WARNING)
        self.reactor = irc.client.Reactor()

        keytext = self.server.crypto.public_key_as_text().splitlines()
        self.nickname = galax.util.filter_str(keytext[1].decode('utf-8'))
        self.channel = galax.util.filter_str(keytext[2].decode('utf-8'))

        self.nickname = self.nickname[-10:]
        self.channel = '#'+self.channel[-10:]

        self.is_connected = False
        self.is_joined = False

        self.connection = self.reactor.server().connect(
            IRC_SERVER,
            IRC_PORT,
            self.nickname
        )

        self.connection.add_global_handler("welcome", self.on_connect)
        self.connection.add_global_handler("join", self.on_join)
        self.connection.add_global_handler("pubmsg", self.on_msg)

        _thread.start_new_thread(self.reactor.process_forever, ())

        logger.info("Initialized Irc Channel...")


    def on_connect(self, connection, event):
        logger.info("Connected to server")
        logger.info("Generated nickname: {}".format(self.nickname))
        logger.info("Generated channel: {}".format(self.channel))

        self.is_connected = True

        if irc.client.is_channel(self.channel):
            connection.join(self.channel)
            return


    def on_join(self, connection, event):
        self.is_joined = True
        logger.info("Joined channel")


    def on_msg(self, connection, event):
        self.recv_callback(event.source, event.arguments[0])


    def send_encrypted(self, msg):
        msg = self.server.crypto.encrypt(msg).decode('utf-8')
        parts = galax.util.chunks(msg, 256)

        while not (self.is_connected and self.is_joined):
            time.sleep(1)

        for part in parts:
            self.connection.privmsg(self.channel, part)


    def send_plaintext(self, msg):
        parts = galax.util.chunks(msg, 256)

        while not (self.is_connected and self.is_joined):
            time.sleep(1)

        for part in parts:
            self.connection.privmsg(self.channel, part)


    def cleanup(self):
        self.connection.quit()
