# galaxcnc
Galax Command &amp; Control server using IRC as backend for exchanging encrypted communications.

## Introduction

The server is able to exchange plaintext messages with clients on a trusted channel. It can also set up a secure channel on top of an untrusted one. The server is independent of the workers and can only ensure the security of its own messages and its own ability to receive secure messages. Workers can adopt the same communication protocol to enjoy full benefits of communicating via secure channel, or they can send and react to arbitrary messages, depending on the needs.

The design is modular, so the server can have many communication channels at its disposal, provided they extend the base Channel class and implement certain functionality.

Since messages are exchanged by text, the workers can be implemented in any programming language.

## Setup

Python 3.5.2 is required.

Create a virtual environment and install dependencies by running `pip install -r requirements.txt`.

`python galax/galax.py` to run the server.

`python -m galax.beacon.beacon` to run the example minimal worker.
