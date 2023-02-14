import sys
from datetime import datetime
# datetime.fromtimestamp(TIMESTAMP)

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


def readFile(numBytes):
    # with open(fileName, mode='rb') as file: # b is important -> binary
    #     return file.read(numBytes)
    return f.read(numBytes)

def compactSize():
    b = readFile(1) # read first byte
    dec = int.from_bytes(b)
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
        self.transactions.getTXInput_Count()

class Header: # header class 
    def __init__(self):
        self.version = None
        self.prev_hash = None
        self.merkle_root_hash = None
        self.time = None
        self.nBits = None
        self.nonce = None
    def getVersion(self):
        bytes = readFile(4)
        self.version = int.from_bytes(bytes, 'little')
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
        bytes = readFile(4)
        print("here", bytes)
        self.nBits = int.from_bytes(bytes, 'big', signed=False)
    def getNonce(self):
        bytes = readFile(4)
        self.nonce = int.from_bytes(bytes, 'little', signed=False)

class TransactionInput:
    def __init__(self):
        self.hash = None
        self.index = None
        self.in_script_bytes = None
        self.signature_script = None
        self.sequence = None

    def getHash(self):
        self.hash = int.from_bytes(readFile(32),'little')
    def getIndex(self):
        self.hash = int.from_bytes(readFile(4),'little')
    def getInScriptBytes(self):
        self.in_script_bytes = compactSize()
        print("in_script_bytes: ", self.in_script_bytes)
    def getSignatureScript(self):
        self.signature_script = int.from_bytes(readFile(self.in_script_bytes),'little') # is this in decimal or hex?
    def getSequence(self):
        self.sequence = int.from_bytes(readFile(4))


class Transaction:
    def __init__(self):
        self.version = None
        self.tx_in_count = None
        self.tx_in = None
        self.tx_out_count = None
        self.tx_out = None
        self.lock_time = None

    def getVersion(self):
        self.version = int.from_bytes(readFile(4), 'little')
    
    def getTXInput_Count(self):
        self.tx_in_count = compactSize()

    # def getTransactionInput(self):
        
    
        

    def getTXInputs(self):
        self.tx_in = []
        for _ in range(self.tx_in_count):
            tr = TransactionInput()
            tr.getHash()
            tr.getIndex()
            tr.getInScriptBytes()
            tr.getSignatureScript()
            tr.getSequence()
            tr.getTransactionInput()
        
            self.tx_in.append(tr)
    
    def getLockTime(self):
        self.lock_time = int.from_bytes(readFile(4), 'little')




bl = Block()
bl.getPreamble()
bl.getHeader()
bl.getTransactions()

print("magic_number", bl.preamble.magic_number)
print("size: ", bl.preamble.size)
print("header version ", bl.header.version)
print("header prev hash", bl.header.prev_hash)
print("merkle_root_hash: ", bl.header.merkle_root_hash)
print("time: ", bl.header.time)
print("nBits", bl.header.nBits)
print("nonce", bl.header.nonce)

# print("tx_in_count: ", bl.transactions.tx_in_count)
# print("prev_hash", bl.header.prev_hash)

f.close()






