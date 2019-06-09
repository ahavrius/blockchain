import datetime
import hashlib
from fastecdsa import keys, curve, ecdsa
#import client
from fastecdsa.encoding.sec1 import SEC1Encoder #decode_public_key, encode_public_key
import json
import os
import ast

QUEUE_FOLDER = 'Pool/'
NULL_BYTE = b'\x00'
NOT_SIGNED = 0

def get_number(min, max, string):
    try:
        number = int(input('Please write {0} between {1} and {2} : '.format(string, min, max)))
    except ValueError:
        raise Exception('Error : {} should be int'.format(string))
    if  number < min or number > max:
        raise Exception('Error : {0} should be between {1} and {2} '.format(string, min, max))
    return number

def get_address():
    address = input('Write an address : ')
    byte_address = ast.literal_eval(address)
    if not isinstance(byte_address, bytes):
        raise Exception('Error : input the wrong address, please use bytecode')
    return byte_address

def add_to_queue(transaction):
    fname  = QUEUE_FOLDER + transaction._timestamp.strftime("%H.%M.%S") + '.json'
    with open(fname, 'a') as f:
        json.dump(transaction.__dict__(), f)

def json_to_transaction(json_data):
    transaction = Transaction(  ast.literal_eval(json_data['from']),
                                ast.literal_eval(json_data['to']),
                                int(json_data['amount']))
    #transaction._timestamp = datetime.strptime(json_data['time'])
    transaction._timestamp = json_data['time']
    transaction._signature = eval(json_data['signature'])
    if not isinstance(transaction._from, bytes) or not isinstance(transaction._to, bytes):
        raise Exception('Error : the wrong address, please use bytecode')
    return transaction

def get_from_queue():
    entries = os.listdir(QUEUE_FOLDER)
    if len(entries) == 0:
        raise Exception('Error : nothing to mine')
    fname = QUEUE_FOLDER + entries[0]
    with open(fname) as json_file:  
        data = json.load(json_file)
    transaction = json_to_transaction(data)
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
        to_hash = str(self)
        sha = hashlib.sha256()
        sha.update(to_hash.encode('utf-8'))
        return sha.hexdigest()

    def __str__(self):
        return ";".join([
                            str(self._from),
                            str(self._to),
                            str(self._amount),
                            str(self._timestamp)])
    def show(self):
        print("".join([
                'Generated transaction : ',
                '\n From the member: ', str(self._from),
                '\n To the member: ',   str(self._to),
                '\n With amount : ',    str(self._amount),
                '\n at : ',             str(self._timestamp)]))

    def is_signed(self):
        return self._signature != NOT_SIGNED

    def check_signature(self):
        if self._from == NULL_BYTE:
            return True
        if not self.is_signed():
            return False
        to_sign = self.calculate_hash()  
        return ecdsa.verify(self._signature, to_sign, SEC1Encoder.decode_public_key(self._from, curve=curve.P256))

    def send(self):
        if not self.check_signature():
            raise Exception('Error : you need to sign transaction before sending')
        add_to_queue(self)
        print('Transaction was successfully added to the queue')

    