import datetime
import hashlib
from fastecdsa import keys, curve, ecdsa
#import client
from fastecdsa.encoding.sec1 import SEC1Encoder #decode_public_key, encode_public_key
import json
import os

QUEUE_FOLDER = 'Pool/'

NOT_SIGNED = 0

def get_amount():
    
    try:
        n = int(input('How much to send? Please write positive number : '))
        if (n <= 0):
            raise Exception('Error : amount should be a positive number')
        return n
    except ValueError:
        raise Exception('Error : amount should be a positive number')

def get_recipient():
    address = input('Write address of recipient : ')
    return address

def add_to_queue(transaction):
    fname  = QUEUE_FOLDER + transaction._timestamp.strftime("%H.%M.%S") + '.json'
    with open(fname, 'a') as f:
        json.dump(transaction.__dict__(), f)
    get_from_queue().show()

def get_from_queue():
    entries = os.listdir(QUEUE_FOLDER)
    if len(entries) == 0:
        raise Exception('nothing to mine')
    #sort ?
    fname = QUEUE_FOLDER + entries[0]
    with open(fname) as json_file:  
        data = json.load(json_file)
    transaction = Transaction(data['from'],
                                data['to'],
                                data['amount'])
    transaction._timestamp = data['time']
    transaction._signature = data['signature']
    #print(SEC1Encoder.decode_public_key(transaction._from, curve=curve.P256))
    #print(eval(transaction._signature))
    os.remove(fname)

    return transaction

class Transaction():
    """
    _from    : string
    _to      : string
    _amount  : int
    _timestamp : datetime
    _signature
    """
    def __init__(self, _from, _to, _amount):
        self._from = _from
        self._to = _to
        self._amount = _amount
        self._signature = NOT_SIGNED
        self._timestamp = datetime.datetime.now()

    def __dict__(self):
        tran = {}
        tran['from']    = str(self._from)
        tran['to']      = str(self._to)
        tran['amount']  = str(self._amount)
        tran['time']    = str(self._timestamp)
        tran['signature'] = str(self._signature)
        return tran

    def calculate_hash(self):
        to_hash = "".join([
                            str(self._from),
                            str(self._to),
                            str(self._amount),
                            str(self._timestamp)])
        sha = hashlib.sha256()
        sha.update(to_hash.encode('utf-8'))
        return sha.hexdigest()

    def show(self):
        print('Generated transaction : ',
                '\n From the member: ', self._from,
                '\n To the member: ', self._to,
                '\n With amount : ', self._amount,
                '\n at : ', self._timestamp)

    def is_signed(self):
        return self._signature != NOT_SIGNED

    def check_signature(self):
        if not self.is_signed():
            return 0
        to_sign = self.calculate_hash()  
        return ecdsa.verify(self._signature, to_sign, SEC1Encoder.decode_public_key(self._from, curve=curve.P256))

    def send(self):
        if not self.check_signature():
            raise Exception('Error : you need to sign transaction before sending')
        add_to_queue(self)
        print('Transaction was successfully added to the queue')

    