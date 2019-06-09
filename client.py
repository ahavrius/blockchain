import datetime
import hashlib
from transaction import *

difficulty_hash = 0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
blockchain_file = 'block.chain'

class Block:

    def __init__(self, data, prev_hash):
        self._data = data
        self._prev_hash = prev_hash
        self._nonce = 0
        self._timestamp = datetime.datetime.now()
        self._hash = self.calculate_hash()

    def __dict__(self):
        dc = {}
        dc["data"]      = str(self._data)
        dc["prev_hash"] = str(self._prev_hash)
        dc["nonce"]     = str(self._nonce)
        dc["timestamp"] = str(self._timestamp)
        dc["hash"]      = str(self._hash)
        return dc

    def __str__(self):
        return json.dumps(self.__dict__())

    def calculate_hash(self):
        to_hash = "".join([
                            str(self._data),
                            str(self._prev_hash),
                            str(self._nonce),
                            str(self._timestamp)])
        sha = hashlib.sha256()
        sha.update(to_hash.encode('utf-8'))
        return sha.hexdigest()

    def is_valid(self):
        if self._data.check_signature() == 0:
            return 0
        return self._hash == self.calculate_hash()

    def proof_of_work(self, difficulty):
        while int(self._hash, 16) >= difficulty_hash:
            self._nonce += 1
            self._hash = self.calculate_hash()

class Blockchain:

    def __init__(self):
        self._chain = [self.genesis_block()]
        self.get_blockchain_from_file()
        self._difficulty = difficulty_hash
        self._mining_reward = 10

    def genesis_block(self):
        return Block(0, 0)

    def chain_height(self):
        return len(self._chain)

    def block_by_id(self):
        id = get_number(0, self.chain_height() - 1, 'index')
        return str(self._chain[id])

    def block_by_hash(self, hash):
        pass

    def last_block_hash(self):
        return self._chain[-1]._hash

    def balance_by_address(self):
        address = get_address()
        balance = 0
        for block in self._chain:
            if type(block._data) is Transaction and block._data._from == address:
                balance -= block._data._amount
            if type(block._data) is Transaction and block._data._to == address:
                balance += block._data._amount
        return balance
    
    def history_by_address(self):
        address = get_address()
        print('History : \n')
        for block in self._chain:
            if type(block._data) is Transaction and \
                address in (block._data._from, block._data._to):
                print(block._data, '\n')
        return ''
        
    def mine_block(self):
        try:
            address = get_address()
            new_transaction = get_from_queue()
            new_transaction.check_signature()
            new_block = Block(new_transaction, self.last_block_hash())
            new_block.proof_of_work(self._difficulty)
            self._chain.append(new_block)
            #add to block.chain file
            #add reward
            revard_transaction = Transaction(NULL_BYTE, address, 1)
            add_to_queue(revard_transaction)
            return('Successfully mined')
        except Exception as err:
            print(err, ', mining was canceled')

    def get_blockchain_from_file(self):
        pass

    def is_chain_valid(self):
        prev_hash = 0
        for block in self._chain:
            if block._hash != block.calculate_hash() or \
                block._prev_hash != prev_hash:
                return False #excrption
            prev_hash = block._hash
        return True

    usage = {
            '-height' : chain_height,
            '-last-hash' : last_block_hash,
            '-info-id' : block_by_id,
            '-info-hash' : block_by_hash,
            '-balance-address' : balance_by_address,
            '-history-address' : history_by_address,
            '-mine' : mine_block,
            '-valid' : is_chain_valid}

def help():
    print('Usage : wallet.py\n',
            ' -exit             :press to terminate program\n',
            ' --help            :press to get the usage\n',
            ' -height           :get the current blockchain height\n',
            ' -last-hash        :get the hash of the last block\n',
            ' -info-id          :display info of the block by id\n',
            ' -info-hash        :display info of the block by hash\n',
            ' -balance-address  :get the balance by adress\n',
            ' -history-address  :display history of all transaction of any address\n',
            ' -mine             :mine transaction from the queue\n',
            ' -valid            :check if the chain is valid')

me = Blockchain()
line = input('Hey, user! Please, write a command (use --help to see usage)\n')

try:
    while not line == '-exit':
        if line == '--help':
            help()
        elif line in Blockchain.usage.keys():
            print(Blockchain.usage[line](me))
        else:
            print('Please, write a valid instraction')
        line = input('')

except Exception as err:
    print('Terminated by ', err)
