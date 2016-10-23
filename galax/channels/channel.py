"""
Channel template

Defines methods of a communications channel.
"""

class Channel(object):
    def __init__(self, server, recv_callback):
        """Constructor.
        Receives a reference to the server, and a callback to be called when
        there's a new message received by the channel.
        Needs to be called by subclasses.
        """
        self.server = server
        self.recv_callback = recv_callback


    def send_encrypted(self, msg):
        """Send an encrypted message through the channel.
        """
        pass


    def send_plaintext(self, msg):
        """Send a plain text message through the channel.
        """
        pass


    def cleanup(self):
        """Free any resources that need special handling.
        """
        pass
