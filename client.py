from blockchain import *

def help():
    print('Usage : client.py\n',
            ' -exit             :press to terminate program\n',
            ' --help            :press to get the usage\n',
            ' -height           :get the current blockchain height\n',
            ' -last-hash        :get the hash of the last block\n',
            ' -info-id          :display info of the block by id\n',
            ' -info-hash        :display info of the block by hash\n',
            ' -balance          :get the balance by adress\n',
            ' -history          :display history of all transaction of any address\n',
            ' -mine             :mine transaction from the queue\n',
            ' -valid            :check if the chain is valid')

me = Blockchain()
line = input('Hey, user of Client Interface! Please, write a command (use --help to see usage)\n')

try:
    while not line == '-exit':
        if line == '--help':
            help()
        elif line in Blockchain.usage.keys():
            answer = Blockchain.usage[line](me)
            if answer is not None:
                print(answer)
        else:
            print('Please, write a valid instraction')
        line = input('')

except Exception as err:
    print('Terminated by ', err)
