import datetime as date
from block import Block, nextBlock
import campcoin_api as campcoin
import simplejson as json
import requests
import time
from lib.prefix import Prefix
from transaction import *
from lib.keys import getEncodedKeys
import os
import urllib.parse
import sys

public_key, _ = getEncodedKeys()
server = "https://campcoin.herokuapp.com"
prefix = Prefix()
campcoin = campcoin.CampCoin("https://campcoin.herokuapp.com")
blockchain = []
currentBlock = campcoin.getCurrentBlock()
nonce = 10000000000
req = requests.get(server + '/api/current').json()
noncecheck = req['nonce']

blockchain.append(currentBlock)

# Genesis Block

def getCurrentBlock():
    req = requests.get(server + '/api/current').json()
    currentBlock = Block(req['index'], req['transactions'], req['nonce'], req['previousHash'], req['hash'])
    return currentBlock

def getCurrentTransactions():
    transactions = requests.get(server + '/api/transactions').json()
    transaction = Transaction("MINER", public_key, 1)
    transactions.append(transaction)
    return transactions

def mineText(previousBlock, transactions, newBlock):
    req = requests.get(server + '/api/current').json()
    os.system("cls")
    print("Previous hash: " + str(req['previousHash']))
    print("")
    print("Transactions: " + str(req['transactions']))
    print("")
    print("Last nonce: " + str(req['nonce']))
    print("")
    print("Current hash: " + str(req['hash']))
    print("")
    print("Current nonce: " + str(nonce))

def mineCycle():
    prefix.fetch()
    try:
        while True:
            newBlock = mine(getCurrentBlock(), getCurrentTransactions())
            submitNewBlock(newBlock)
    except KeyboardInterrupt:
        pass

def submitNewBlock(newBlock):
    req = requests.post(server + '/api/mine', json=newBlock)
    if req.status_code == 200:
        os.system("cls")
        print("Block Mined!")
        global nonce
        nonce = 10000000000
        time.sleep(3)

# The campcoin API endpoint is https://campcoin.herokuapp.com/api/current

def mine(previousBlock, transactions):
    global nonce
    nonce = 10000000000
    newBlock = nextBlock(previousBlock, json.dumps(transactions), nonce)
    mineText(previousBlock, transactions, newBlock)

    beginTimestamp = date.datetime.now()
    while (not newBlock.validate(prefix.get())):
        nonce = nonce + 1
        newBlock = nextBlock(previousBlock, json.dumps(transactions), nonce)
        if not newBlock.validate(prefix.get()):
            nonce = nonce * 2
            newBlock = nextBlock(previousBlock, json.dumps(transactions), nonce)
            if not newBlock.validate(prefix.get()):
                nonce = nonce / 2
        if ((date.datetime.now() - beginTimestamp).total_seconds() > 5):
            beginTimestamp = date.datetime.now()
            previousBlock = getCurrentBlock()
            transactions = getCurrentTransactions()
            prefix.fetch()
            mineText(previousBlock, transactions, newBlock)
    return newBlock

def checkBalance():
    key = {'public_key': public_key}
    req = requests.get(server + '/api/balance?' + urllib.parse.urlencode(key))
    os.system('cls')
    print("Key: " + public_key)
    print("Balance: " + req.text)
    print("")
    input("Press enter to return to menu...")

while 1:
    os.system("cls")
    mode = input("Mode: ")
    if mode.lower() == "mine":
        mineCycle()
    if mode.lower() == "balance":
        checkBalance()
    if mode.lower() == "exit":
        sys.exit(0)
