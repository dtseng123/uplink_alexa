# coding=utf-8

# uplink
# By Darren Tseng <darren@adjoint.io>
#
# Uplink blockchain integration with Alexa
import os
import logging
from datetime import datetime
from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement
from uplink import *
from uplink.session import UplinkSession

__author__ = 'Darren Tseng'
__email__ = 'darren@adjoint.io'
rpc_addr = os.environ.get('RPC_HOST', 'localhost')


app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


uplink = UplinkSession(addr=rpc_addr)

uplink.init_app(app)

# Session starter
#
# This intent is fired automatically at the point of launch (= when the session starts).
# Use it to register a state machine for things you want to keep track of, such as what the last intent was, so as to be
# able to give contextual help.


@ask.on_session_started
def start_session():
    """
    Fired at the start of the session, this is a great place to initialise state variables and the like.
    """
    logging.debug("Session started at {}".format(datetime.now().isoformat()))

# Launch intent
#
# This intent is fired automatically at the point of launch.
# Use it as a way to introduce your Skill and say hello to the user. If you envisage your Skill to work using the
# one-shot paradigm (i.e. the invocation statement contains all the
# parameters that are required for returning the

# result


@ask.launch
def handle_launch():
    """
    (QUESTION) Responds to the launch of the Skill with a welcome statement and a card.

    Templates:
    * Initial statement: 'welcome'
    * Reprompt statement: 'welcome_re'
    * Card title: 'uplink
    * Card body: 'welcome_card'
    """

    welcome_text = render_template('welcome')
    welcome_re_text = render_template('welcome_re')
    welcome_card_text = render_template('welcome_card')

    return question(welcome_text).reprompt(welcome_re_text).standard_card(title="uplink",
                                                                          text=welcome_card_text)


@ask.intent('getPeersIntent')
def getPeers():
    try:
        peers = len(uplink.peers())
    except RpcConnectionFail:
        peers = 0

    speech_text = ""

    if peers == 0:
        speech_text = "There are not any nodes on the network. You are not connected to uplink."

    if peers == 1:
        speech_text = "There is 1 node on the Uplink network."

    if peers > 1:
        speech_text = "There are {} nodes on the network".format(peers)

    return statement(speech_text).simple_card('Peers:', speech_text)


@ask.intent('getBlocksIntent')
def getBlocks():
    blocks = uplink.blocks()
    number_of_blocks = len(blocks)

    if number_of_blocks == 1:
        text = "There is only the genisis block."
    else:
        text = "There are currently {} validated blocks. If you would like to introspect the details of a block, for example, say look at block number 2".format(
            number_of_blocks)

    return statement(text).simple_card("Blocks", text)


@ask.intent('getBlockIntent')
def getBlock(block_num):
    blocks = uplink.blocks()
    block_tx = len(blocks[int(block_num)].transactions)

    if block_tx == 0:
        text = "This is the genisis block. Try a different one."

    if block_tx == 1:
        text = "There is 1 transaction in block {}".format(block_num)

    if block_tx > 1:
        text = "There are {} validated transactions in block {}".format(
            block_tx, block_num)

    return statement(text).simple_card("Block details:", text)

# Built-in intents
#
# These intents are built-in intents. Conveniently, built-in intents do not need you to define utterances, so you can
# use them straight out of the box. Depending on whether you wish to implement these in your application, you may keep
# or delete them/comment them out.
#
# More about built-in intents: http://d.pr/KKyx


@ask.intent('AMAZON.StopIntent')
def handle_stop():
    """
    (STATEMENT) Handles the 'stop' built-in intention.
    """
    farewell_text = render_template('stop_bye')
    return statement(farewell_text)


@ask.intent('AMAZON.CancelIntent')
def handle_cancel():
    """
    (STATEMENT) Handles the 'cancel' built-in intention.
    """
    farewell_text = render_template('cancel_bye')
    return statement(farewell_text)


@ask.intent('AMAZON.HelpIntent')
def handle_help():
    """
    (QUESTION) Handles the 'help' built-in intention.

    You can provide context-specific help here by rendering templates conditional on the help referrer.
    """

    help_text = render_template('help_text')
    return question(help_text)


@ask.intent('AMAZON.NoIntent')
def handle_no():
    """
    (?) Handles the 'no' built-in intention.

    """
    pass


@ask.intent('AMAZON.YesIntent')
def handle_yes():
    """
    (?) Handles the 'yes'  built-in intention.
    """
    pass


@ask.intent('AMAZON.PreviousIntent')
def handle_back():
    """
    (?) Handles the 'go back!'  built-in intention.
    """
    pass


@ask.intent('AMAZON.StartOverIntent')
def start_over():
    """
    (QUESTION) Handles the 'start over!'  built-in intention.
    """
    pass


# Ending session
#
# This intention ends the session.

@ask.session_ended
def session_ended():
    """
    Returns an empty for `session_ended`.

    .. warning::

    The status of this is somewhat controversial. The `official documentation`_ states that you cannot return a response
    to ``SessionEndedRequest``. However, if it only returns a ``200/OK``, the quit utterance (which is a default test
    utterance!) will return an error and the skill will not validate.

    """
    return statement("")


if __name__ == '__main__':
    app.run(debug=True)
