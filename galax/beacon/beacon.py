import argparse
import base64
import binascii
import json
import os
import random
import string
import time
import _thread

import irc
import irc.client
import requests

import galax.util
from galax.cryptotools import deserialize_public_key, encrypt

PUB_KEY_FILE = "pubkey.pem"
IRC_SERVER = "chat.freenode.net"
IRC_PORT = 6667


class GalaxBeacon(object):
    """Simple worker that broadcasts the ip of the machine it's running on
    every minute.
    """
    def __init__(self, pubkey, delay=60):
        self.pubkey = pubkey
        self.delay = delay
        with open(pubkey, 'rb') as keyfile:
            self.pubkey = keyfile.readlines()


        self.pubkey = "".join([x.decode('utf-8') for x in self.pubkey])

        self.nickname = ''.join([random.choice(string.ascii_letters) for x in
                                 range(10)])
        self.channel = \
        '#' + galax.util.filter_str(self.pubkey.splitlines()[2])[-10:]

        self.pubkey = deserialize_public_key(self.pubkey.encode('utf-8'))

        self.is_connected = False
        self.is_joined = False

        self.reactor = irc.client.Reactor()
        self.connection = self.reactor.server().connect(
            IRC_SERVER,
            IRC_PORT,
            self.nickname
        )

        self.connection.add_global_handler("welcome", self.on_connect)
        self.connection.add_global_handler("join", self.on_join)

        _thread.start_new_thread(self.reactor.process_forever, ())


    def on_connect(self, connection, event):
        self.is_connected = True
        if irc.client.is_channel(self.channel):
            connection.join(self.channel)


    def on_join(self, connection, event):
        self.is_joined = True


    def send_encrypted(self, msg):
        msg = encrypt(msg, self.pubkey).decode('utf-8')

        #Generate an id
        hash = ''.join([random.choice(string.ascii_letters) for x in range(8)])

        # Divide into 128-byte chunks, wrap in json, and encode with base64
        parts = list(galax.util.chunks(msg, 128))
        parts = [base64.urlsafe_b64encode(json.dumps(
            {
                'id': hash,
                'part': i,
                'total':len(parts),
                'content': part
            }).encode('utf-8')
        ).decode('utf-8') for (i, part) in enumerate(parts)]


        while not (self.is_connected and self.is_joined):
            time.sleep(1)

        for part in parts:
            self.connection.privmsg(self.channel, part)


    def get_public_ip(self):
        return requests.get('https://api.ipify.org').text


    def run(self):
        print("Beacon ready and starting to run")
        try:
            while True:
                self.send_encrypted("My IP is:"
                                    " {}".format(self.get_public_ip()))
                time.sleep(self.delay)
        except KeyboardInterrupt:
            print("Received Ctrl-C, quitting")
            self.connection.quit()
            exit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--delay', help='delay between subsequent messages, in'
                        'seconds. default is 60', default=60)
    args = parser.parse_args()

    gb = GalaxBeacon(PUB_KEY_FILE, delay=int(args.delay))
    gb.run()


if __name__=='__main__':
    main()
