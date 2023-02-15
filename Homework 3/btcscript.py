import sys
from datetime import datetime
import json
from collections import defaultdict
# datetime.fromtimestamp(TIMESTAMP)

jd = {}
jd["blocks"] = []

error_lookup = {
    1 : "Invalid magic number",
    2 : "Invalid header version",
    3 : "Invalid previous header hash",
    4 : "Invalid timestamp",
    5 : "Invalid transaction version",
    6 : "The Merkle tree hash in the header is incorrect"
}



def readFile(numBytes):
    # with open(fileName, mode='rb') as file: # b is important -> binary
    #     return file.read(numBytes)
    return f.read(numBytes)

def compactSize():
    b = readFile(1) # read first byte
    dec = int.from_bytes(b)
    # print("DEBUG dec: ", dec,b)
    if dec >= 0 and dec < 253:
        return dec
    elif dec == 253:
        return int.from_bytes(readFile(2), 'little')
    elif dec == 254:
        return int.from_bytes(readFile(4), 'little')
    else:
        return int.from_bytes(readFile(8), 'little')



class Preamble:
    def __init__(self):
        self.magic_number = None
        self.size = None
    def getMagicNumber(self):
        bytes = readFile(4)
        self.magic_number = int.from_bytes(bytes, 'little')
    def getSize(self):
        bytes = readFile(4)
        self.size = int.from_bytes(bytes, 'little')


class Block:
    def __init__(self):
        self.preamble = None
        self.header = None
        self.txn_count = None
        self.transactions = None

    def getPreamble(self): # order matters
        self.preamble = Preamble()
        self.preamble.getMagicNumber()
        self.preamble.getSize()
    def getHeader(self): # order matters
        self.header = Header()
        self.header.getVersion()
        self.header.getPrevHash()
        self.header.getMerkleRootHash()
        self.header.getTime()
        self.header.GetnBits()
        self.header.getNonce()
    def getTransactions(self):
        self.transactions = Transaction()

        self.transactions.getVersion()
        self.transactions.getTXInput_Count()
        self.transactions.getTXInputs()
        self.transactions.getTXOutput_Count()
        self.transactions.getTXOutputs()
        self.transactions.getLockTime()

    def getTransactionCount(self):
        self.txn_count = compactSize()

class Header: # header class 
    def __init__(self):
        self.version = None
        self.prev_hash = None
        self.merkle_root_hash = None
        self.time = None
        self.nBits = None
        self.nonce = None
    def getVersion(self):
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        self.version = int.from_bytes(bytes(bytes_array))

    def getPrevHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse() # reverse the endianess of these bytes
        self.prev_hash = str(bytes(bytes_array).hex())
    def getMerkleRootHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse()
        self.merkle_root_hash = str(bytes(bytes_array).hex())
    def getTime(self):
        bytes = readFile(4)
        self.time = int.from_bytes(bytes, 'little', signed=False)
    def GetnBits(self):
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        # self.nBits = int.from_bytes(bytes, 'big', signed=False)
        self.nBits = bytes(bytes_array).hex()
    def getNonce(self):
        bytes = readFile(4)
        self.nonce = int.from_bytes(bytes, 'little', signed=False)

class TransactionOutput:
    def __init__(self):
        self.value = None
        self.out_script_bytes = None
        self.out_script = None
    def getValue(self):
        self.value = int.from_bytes(readFile(8), 'little')
    def getOutScriptBytes(self):
        self.out_script_bytes = compactSize()
    def getOutScript(self):
        self.out_script = readFile(self.out_script_bytes).hex()

class TransactionInput:
    def __init__(self):
        self.utxo_hash = None
        self.index = None
        self.in_script_bytes = None
        self.signature_script = None
        self.sequence = None
    def getHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse()
        self.utxo_hash = str(bytes(bytes_array).hex())
    def getIndex(self):
        self.index = int.from_bytes(readFile(4),'little')
    def getInScriptBytes(self):
        self.in_script_bytes = compactSize()
        # print("in_script_bytes: ", self.in_script_bytes)
    def getSignatureScript(self):
        # bytes_array = bytearray(readFile(32))
        self.signature_script = readFile(self.in_script_bytes).hex()
        # self.signature_script = int.from_bytes(readFile(self.in_script_bytes),'little') # is this in decimal or hex?
    def getSequence(self):
        self.sequence = int.from_bytes(readFile(4))


class Transaction:
    def __init__(self):
        self.version = None
        self.tx_in_count = None
        self.tx_in = []
        self.tx_out_count = None
        self.tx_out = []
        self.lock_time = None

    def getVersion(self):
        # self.version = int.from_bytes(readFile(4), 'little')
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        # self.version = int.from_bytes(bytes, 'little', signed=True)
        self.version = int.from_bytes(bytes(bytes_array))

    def getTXInput_Count(self):
        self.tx_in_count = compactSize()

    def getTXInputs(self):
        for _ in range(self.tx_in_count):
            tr = TransactionInput()
            tr.getHash()
            tr.getIndex()
            tr.getInScriptBytes()
            tr.getSignatureScript()
            tr.getSequence()
            self.tx_in.append(tr)
    
    def getTXOutput_Count(self):
        self.tx_out_count = compactSize()
        
    def getTXOutputs(self):
        for _ in range(self.tx_out_count):
            tr = TransactionOutput()
            tr.getValue()
            tr.getOutScriptBytes()
            tr.getOutScript()
            self.tx_out.append(tr)        
    def getLockTime(self):
        self.lock_time = int.from_bytes(readFile(4), 'little')

fileName = sys.argv[1]
f = open(fileName, mode='rb')

# while f.read() != "":
bl = Block()
bl.getPreamble()
bl.getHeader()
bl.getTransactionCount()
for _ in range(bl.txn_count):
    bl.getTransactions()






with open('output.txt', 'w') as file:
    sys.stdout = file # Change the standard output to the file we created.


    json_d = json.loads(jd)

    print("magic_number", bl.preamble.magic_number) #preamble
    print("size: ", bl.preamble.size)

    print("header version ", bl.header.version) # header
    print("header prev hash", bl.header.prev_hash)
    print("merkle_root_hash: ", bl.header.merkle_root_hash)
    print("time: ", bl.header.time)
    print("nBits", bl.header.nBits)
    print("nonce", bl.header.nonce) 

    print("transaction version: ", bl.transactions.version) # transaction
    print("tx_in_count: ", bl.transactions.tx_in_count)

    # print("tx_inputs: ", bl.transactions.tx_in)
    print("tx_inputs: ")
    for i in range(bl.transactions.tx_in_count):
        print("utxo_hash: ", bl.transactions.tx_in[i].utxo_hash)
        print("index: ", bl.transactions.tx_in[i].index)
        print("in_script_bytes: ", bl.transactions.tx_in[i].in_script_bytes)
        print("signature script: ", bl.transactions.tx_in[i].signature_script)
        print("sequence: ", bl.transactions.tx_in[i].sequence)
    print("tx_output_count: ")
    for i in range(bl.transactions.tx_out_count):
        print("satoshis: ", bl.transactions.tx_out[i].value)
        print("out_script_bytes: ", bl.transactions.tx_out[i].out_script_bytes)
        print("out_script: ", bl.transactions.tx_out[i].out_script)
    print("locktime: ", bl.transactions.lock_time)





f.close()








