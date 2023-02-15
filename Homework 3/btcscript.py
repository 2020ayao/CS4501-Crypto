import sys
from datetime import datetime
import json
from collections import defaultdict
# datetime.fromtimestamp(TIMESTAMP)

d = {}
d["blocks"] = []

error_lookup = {
    1 : "Invalid magic number",
    2 : "Invalid header version",
    3 : "Invalid previous header hash",
    4 : "Invalid timestamp",
    5 : "Invalid transaction version",
    6 : "The Merkle tree hash in the header is incorrect"
}


fileName = sys.argv[1]
f = open(fileName, mode='rb')
bytes_master = f.read()
# print(type(bytes_master))
f.close()


def readFile(numBytes):
    global bytes_master
    # with open(fileName, mode='rb') as file: # b is important -> binary
    #     return file.read(numBytes)
    res = bytes_master[:numBytes]
    bytes_master = bytes_master[numBytes:]
    return res

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
    def __init__(self, height):
        # self.preamble = None
        # self.header = None
        self.height = height
        self.version = None
        self.previous_hash = None
        self.merkle_hash = None
        self.timestamp = None
        self.timestamp_readable = None
        self.nbits = None
        self.nonce = None

        self.txn_count = None
        self.transactions = []

    # def getPreamble(self): # order matters
    #     self.preamble = Preamble()
    #     self.preamble.getMagicNumber()
    #     self.preamble.getSize()
        
    def getHeader(self): # order matters
        # self.header = Header()
        self.getVersion()
        self.getPrevHash()
        self.getMerkleRootHash()
        self.getTime()
        self.getTimereadable()
        self.GetnBits()
        self.getNonce()

    def getTransaction(self):
        tran = Transaction()

        tran.getVersion()
        tran.getTXInput_Count()
        tran.getTXInputs()
        tran.getTXOutput_Count()
        tran.getTXOutputs()
        tran.getLockTime()
        return tran

    def getTransactionCount(self):
        self.txn_count = compactSize()

    # HEADER METHODS
    def getVersion(self):
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        self.version = int.from_bytes(bytes(bytes_array))

    def getPrevHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse() # reverse the endianess of these bytes
        self.previous_hash = str(bytes(bytes_array).hex())
    def getMerkleRootHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse()
        self.merkle_hash = str(bytes(bytes_array).hex())
    def getTime(self):
        bytes = readFile(4)
        self.timestamp = int.from_bytes(bytes, 'little', signed=False)
        # print(self.timestamp)
    def getTimereadable(self):
        self.timestamp_readable = datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # print(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        # self.timestamp_readable = self.timestamp_readable.strftime('%Y-%m-%d %H:%M:%S')

    def GetnBits(self):
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        # self.nbits = int.from_bytes(bytes, 'big', signed=False)
        self.nbits = bytes(bytes_array).hex()
    def getNonce(self):
        bytes = readFile(4)
        self.nonce = int.from_bytes(bytes, 'little', signed=False)


class Header: # header class 
    def __init__(self):
        self.version = None
        self.previous_hash = None
        self.merkle_hash = None
        self.timestamp = None
        self.nbits = None
        self.nonce = None
    def getVersion(self):
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        self.version = int.from_bytes(bytes(bytes_array))

    def getPrevHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse() # reverse the endianess of these bytes
        self.previous_hash = str(bytes(bytes_array).hex())
    def getMerkleRootHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse()
        self.merkle_hash = str(bytes(bytes_array).hex())
    def getTime(self):
        bytes = readFile(4)
        self.timestamp = int.from_bytes(bytes, 'little', signed=False)
    def GetnBits(self):
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        # self.nbits = int.from_bytes(bytes, 'big', signed=False)
        self.nbits = bytes(bytes_array).hex()
    def getNonce(self):
        bytes = readFile(4)
        self.nonce = int.from_bytes(bytes, 'little', signed=False)

class TransactionOutput:
    def __init__(self):
        self.satoshis = None
        self.output_script_size = None
        self.output_script_bytes = None
    def getValue(self):
        self.satoshis = int.from_bytes(readFile(8), 'little')
    def getOutScriptBytes(self):
        self.output_script_size = compactSize()
    def getOutScript(self):
        self.output_script_bytes = readFile(self.output_script_size).hex()

class TransactionInput:
    def __init__(self):
        self.utxo_hash = None
        self.index = None
        self.input_script_size = None
        self.input_script_bytes = None
        self.sequence = None
    def getHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse()
        self.utxo_hash = str(bytes(bytes_array).hex())
    def getIndex(self):
        self.index = int.from_bytes(readFile(4),'little')
    def getInScriptBytes(self):
        self.input_script_size = compactSize()
        # print("input_script_size: ", self.input_script_size)
    def getSignatureScript(self):
        # bytes_array = bytearray(readFile(32))
        self.input_script_bytes = readFile(self.input_script_size).hex()
        # self.input_script_bytes = int.from_bytes(readFile(self.input_script_size),'little') # is this in decimal or hex?
    def getSequence(self):
        self.sequence = int.from_bytes(readFile(4))

class Blocks:
    def __init__(self):
        self.blocks = []
        self.height = None

    def toJSON(self):
        # return json.dumps(self, default=lambda o: o.__dict__)
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def getBlock(self, height):
        bl = Block(height)
        # bl.getPreamble()
        bl.getHeader()
        bl.getTransactionCount()
        for _ in range(bl.txn_count):
            bl.transactions.append(bl.getTransaction())
        self.blocks.append(bl)

    def finalizeHeight(self, h):
        self.height = h


class Transaction:
    def __init__(self):
        self.version = None
        self.txn_in_count = None
        self.txn_inputs = []
        self.txn_out_count = None
        self.txn_outputs = []
        self.lock_time = None

    def getVersion(self):
        # self.version = int.from_bytes(readFile(4), 'little')
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        # self.version = int.from_bytes(bytes, 'little', signed=True)
        self.version = int.from_bytes(bytes(bytes_array))

    def getTXInput_Count(self):
        self.txn_in_count = compactSize()

    def getTXInputs(self):
        for _ in range(self.txn_in_count):
            tr = TransactionInput()
            tr.getHash()
            tr.getIndex()
            tr.getInScriptBytes()
            tr.getSignatureScript()
            tr.getSequence()
            self.txn_inputs.append(tr)
    
    def getTXOutput_Count(self):
        self.txn_out_count = compactSize()
        
    def getTXOutputs(self):
        for _ in range(self.txn_out_count):
            tr = TransactionOutput()
            tr.getValue()
            tr.getOutScriptBytes()
            tr.getOutScript()
            self.txn_outputs.append(tr)        
    def getLockTime(self):
        self.lock_time = int.from_bytes(readFile(4), 'little')


# while f.read() != "":



# d["blocks"].append(bl.toJSON())
# print(json.dumps(d))
# json_d = json.dumps(d, indent = 4)








# with open('output.txt', 'w') as file:
#     sys.stdout = file # Change the standard output to the file we created.

#     # print(json.dumps(d,indent=4))


    
#     bigBlock.getBlock(height)
    
#     # json_obj = json.dumps(bigBlock, indent=4)
#     # print(json_obj)

#     # print(d.encode)

#     # print("magic_number", bl.preamble.magic_number) #preamble
#     # print("size: ", bl.preamble.size)

#     # print("header version ", bl.version) # header
#     # print("header prev hash", bl.prev_hash)
#     # print("merkle_root_hash: ", bl.merkle_root_hash)
#     # print("time: ", bl.time)
#     # print("nBits", bl.nBits)
#     # print("nonce", bl.nonce) 

#     # print("transaction version: ", bl.transactions.version) # transaction
#     # print("txn_in_count: ", bl.transactions.txn_in_count)

#     # # print("txn_inputs: ", bl.transactions.txn_in)
#     # print("txn_inputs: ")
#     # for i in range(bl.transactions.txn_in_count):
#     #     print("utxo_hash: ", bl.transactions.txn_in[i].utxo_hash)
#     #     print("index: ", bl.transactions.txn_in[i].index)
#     #     print("sze: ", bl.transactions.txn_in[i].input_script_size)
#     #     print("signature script: ", bl.transactions.txn_in[i].input_script_bytes)
#     #     print("sequence: ", bl.transactions.txn_in[i].sequence)
#     # print("txn_output_count: ")
#     # for i in range(bl.transactions.txn_out_count):
#     #     print("satoshis: ", bl.transactions.txn_out[i].satoshis)
#     #     print("output_script_size: ", bl.transactions.txn_out[i].output_script_size)
#     #     print("output_script_bytes: ", bl.transactions.txn_out[i].output_script_bytes)
#     # print("locktime: ", bl.transactions.lock_time)

# fileName = "blk00000-f10.blk"
file = open(fileName + ".json", mode='w')
bigBlock = Blocks()
height = 0
while len(bytes_master.hex()) > 0:
    
# while f.readline() != "":
    p = Preamble()
    magicNumber = p.getMagicNumber()
    size = p.getSize()
    bigBlock.getBlock(height)
    height += 1

bigBlock.finalizeHeight(height)
file.write(bigBlock.toJSON())


file.close()








