# coding=utf-8

# uplink
# By Darren Tseng <darren@adjoint.io>
#
# Uplink blockchain integration with Alexa
import os
import gevent
import logging
from datetime import datetime
from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement
from uplink import *
# from uplink.cryptography import ecdsa_new, make_qrcode, derive_account_address

from uplink.session import UplinkSession
from uplink.cryptography import read_key, save_key

import humanhash

__author__ = 'Darren Tseng'
__email__ = 'darren@adjoint.io'
rpc_addr = os.environ.get('RPC_HOST', 'localhost')


app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


uplink = UplinkSession(addr=rpc_addr)

uplink.init_app(app)

# TX TYPE
CreateContract = "CreateContract"
CallContract = "Call"
CreateAsset = "CreateAsset"
TransferAsset = "Transfer"
CirculateAsset = "Circulate"
RevokeAsset = "RevokeAsset"
CreateAccount = "CreateAccount"
RevokeAccount = "RevokeAccount"


# Session starter
#
# This intent is fired automatically at the point of launch (= when the session starts).
# Use it to register a state machine for things you want to keep track of, such as what the last intent was, so as to be
# able to give contextual help.

# Move this to a filter module

def datetimeformat(timestamp):
    """Filter for converting timestamp to human readable"""
    return time.strftime('%m/%d/%Y, %I:%M:%S %p', time.localtime(timestamp / 1000000))


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

    # ===================CREATE RENTER ACCOUNT ===================
    pk1, sk1 = ecdsa_new()
    metadata = {
        'name': 'Renter John',
    }
    renter_acct = create_account(metadata=metadata)
    privkey_pem = sk1.to_pem()

    location = "./keys/{}".format("renter-" + renter_acct.address)
    save_key(privkey_pem, location)

    # =================== CREATE LANDLORD ACCOUNT ===================
    pk, sk = ecdsa_new()
    meta = {
        'name': "Landlord Bob"
    }

    landlord_acct = create_account(metadata=meta)

    landlord_hid = humanhash.humanize(landlord_acct.address.encode("hex"))
    renter_hid = humanhash.humanize(renter_acct.address.encode("hex"))

    print("landlord HID: " + landlord_hid + "|" + landlord_acct.address)
    print("renter HID: " + renter_hid + "|" + renter_acct.address)

    privkey_pem = sk.to_pem()
    location = "./keys/{}".format("landlord-" + landlord_acct.address)
    save_key(privkey_pem, location)

    # =================== CREATE ASSET TO USE ======================
    private_key = sk
    origin = landlord_acct.address
    name = "GBP"
    asset_type = "Discrete"
    reference = "Token"
    supply = 100000
    issuer = landlord_acct.address

    asset = create_asset(private_key, origin, name, supply,
                         asset_type, reference, issuer)

    asset_hid = humanhash.humanize(asset.encode("hex"))
    print(asset_hid)

    # =================== CIRCULATE ASSET ======================
    amount = 100000
    receipt = uplink.circulate_asset(private_key, origin, amount, asset)

    gevent.sleep(1)  # :(

    if receipt['tag'] == 'RPCRespOK':
        print(receipt)
    else:
        print("ERROR with circulation")

    # =================== TRANSFER ASSET ================
    balance = 10000
    receipt = uplink.transfer_asset(
        private_key, origin, renter_acct.address, balance, asset)

    gevent.sleep(1)  # :(

    if receipt['tag'] == 'RPCRespOK':
        print(receipt)
    else:
        print("ERROR with Transfer")

    # =================== WELCOME TEXT =====================
    welcome_text = render_template('welcome')
    welcome_re_text = render_template('welcome_re')
    welcome_card_text = render_template('welcome_card')

    return question(welcome_text).reprompt(welcome_re_text).standard_card(title="uplink",
                                                                          text=welcome_card_text)


def create_asset(private_key, origin, name, supply,
                 asset_type, reference, issuer, precision=None):
    """Create Asset"""

    try:
        result, newasset_addr = uplink.create_asset(private_key, origin, name, supply,
                                                    asset_type, reference, issuer, precision)
        count = 0
        while True:
            count += 1
            gevent.sleep(0.2)
            if count > 60:
                print("failed to create account")
            try:
                asset_details = uplink.getasset(newasset_addr)
                print("new asset successfully created " + asset_details.address)
            except UplinkJsonRpcError:
                continue
            break

        return newasset_addr

    except UplinkJsonRpcError as result:
        newasset_addr = ""
        error = result.response.get('contents').get('errorMsg')
        print(error)
        return error


def create_account(pk=None, sk=None, metadata=None):
    """Create Account"""
    if(pk is None):
        pk, sk = ecdsa_new()

    acct = uplink.create_account(
        private_key=sk,
        public_key=pk,
        from_address=None,
        metadata=metadata,
        timezone="GMT"
    )
    count = 0
    while True:
        count += 1
        gevent.sleep(0.2)

        if (count > 60):
            print("failed to create account")
        try:
            acct_detail = uplink.getaccount(acct.address)

            print("new account successfully created " + acct_detail.address)
        except UplinkJsonRpcError:
            continue
        break

    print(acct)
    return acct


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
    block_len = len(blocks)

    if int(block_num) > int(block_len):
        text = "There are {} blocks in this chain, so don't ask for block {}. Try again".format(
            block_len, block_num)
    else:
        block_tx = len(blocks[int(block_num)].transactions)

        if block_tx == 0:
            text = "This is the genisis block. Try a different one."

        if block_tx == 1:
            text = "There is 1 transaction in block {}".format(block_num)

        if block_tx > 1:
            text = "There are {} validated transactions in block {}".format(
                block_tx, block_num)

    return statement(text).simple_card("Block details:", text)


@ask.intent('getTransactionsByBlock')
def getTxBlock(block_num, tx_num):

    blocks = uplink.blocks()
    block_tx = len(blocks[int(block_num)].transactions)

    tx = blocks[int(block_num)].transactions[int(tx_num)]

    timestamp = datetimeformat(tx.get("timestamp"))
    origin = str(tx.get('origin'))
    action = str(tx.get('header').get('contents').get('tag'))
    body = tx.get("header").get('contents').get('contents')
    tx_details = ""

    if action == CreateAccount:
        tz = body.get('timezone')
        tz_text = "Account is associated with timezone {}. ".format(tz)

        if len(body.get("metadata")) > 0:
            meta_txt = ""
            for key, value in body.get('metadata'):
                meta = str(key) + " " + str(value) + ", "
                meta_txt = meta_txt + " " + meta

            meta_txt = "The metadata associated with account contains: {}".format(
                meta_txt)
        else:
            meta_txt = "There isn't any metadata."

        tx_details = tz_text + meta_txt

    if action == CirculateAsset:
        amount = body.get('amount')
        assetAddr = body.get('assetAddr')[:-10]

        asset_hid = humanhash.humanize(assetAddr.encode("hex"))

        tx_details = "{} of asset id: {} was circulated".format(
            amount, asset_hid)

    if action == TransferAsset:
        assetAddr = body.get("assetAddr")
        asset_hid = humanhash.humanize(assetAddr.encode("hex"))
        balance = body.get("balance")
        toAddr = body.get("toAddr")
        account_hid = humanhash.humanize(toAddr.encode("hex"))

        tx_details = "{} of asset ID {}, was transferred to account ID {}.".format(
            balance, asset_hid, account_hid)

    if action == CreateAsset:
        asset_addr = body.get("assetAddr")
        asset_hid = humanhash.humanize(asset_addr.encode("hex"))
        asset_name = body.get("assetName")
        asset_type = body.get("assetType").get("tag")
        reference = body.get("reference")
        supply = body.get("supply")

        if asset_type != "Fractional":
            precision = body.get("assetType").get("contents")
        else:
            precision = None

        tx_details = "Asset {} has a supply of {} with an id of {}".format(
            asset_name, supply, asset_hid)

    if action == CreateContract:
        contract_addr = body.get("address")
        contract_hid = humanhash.humanize(contract_addr.encode("hex"))
        owner_addr = body.get("owner")
        owner_hid = humanhash.humanize(owner_addr.encode("hex"))
        script = body.get("script")
        timestamp = datetimeformat(body.get("timestamp"))

        tx_details = "Contract {} was created on {} by account {}.".format(
            contract_hid, timestamp, owner_hid)

    if action == CallContract:
        contract_addr = body.get("address")
        contract_hid = humanhash.humanize(contract_addr.encode("hex"))
        method = body.get("method")

        tx_details = "Called {} method on contract {}".format(
            method, contract_hid)

    if action == RevokeAsset:
        asset_addr = body.get("address")
        asset_hid = humanhash.humanize(asset_addr.encode("hex"))

        tx_detail = "Asset {} was revoked.".format(asset_hid)

    if action == RevokeAccount:
        acct_addr = body.get("address")
        acct_hid = humanhash.humanize(acct_addr.encode("hex"))

        tx_detail = "Account {} was revoked.".format(acct_hid)

    # Complete Text Output
    text = "{} transaction executed on {}. Here are the details: {}".format(
        action, timestamp, tx_details)

    # return question(text).reprompt('would you like the
    # details?').standard_card('Transactions details?', text)
    return statement(text).simple_card("Transaction Details", text)


# @ask.intent('createAccountIntent')
# def createAccount():


@ask.intent('getAssetIntent')
def getAsset(asset_hid):

    uid = humanhash.uid(asset_hid)
    asset_addr = uid.decode('hex')
    asset = uplink.getasset(asset_addr)
    print()
    text = "hello"
    return statement(text).simple_card("Asset", text)

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
