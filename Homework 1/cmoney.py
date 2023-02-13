import sys
import rsa

import hashlib
import binascii
import rsa

import os.path
from os import path

from datetime import datetime

NAME = "dimedollars (TM)"
sourceFund = "bigfoot"
# gets the hash of a file; from https://stackoverflow.com/a/44873382
def hashFile(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()

# given an array of bytes, return a hex reprenstation of it
def bytesToString(data):
    return binascii.hexlify(data)

# given a hex reprensetation, convert it to an array of bytes
def stringToBytes(hexstr):
    return binascii.a2b_hex(hexstr)

# Load the wallet keys from a filename
def loadWallet(filename): # WHEN DO I NEED TO USE THIS ???????
    with open(filename, mode='rb') as file:
        keydata = file.read()
    privkey = rsa.PrivateKey.load_pkcs1(keydata)
    pubkey = rsa.PublicKey.load_pkcs1(keydata)
    return pubkey, privkey

# save the wallet to a file
def saveWallet(pubkey, privkey, filename):
    # Save the keys to a key format (outputs bytes)
    pubkeyBytes = pubkey.save_pkcs1(format='PEM')
    privkeyBytes = privkey.save_pkcs1(format='PEM')
    # Convert those bytes to strings to write to a file (gibberish, but a string...)
    pubkeyString = pubkeyBytes.decode('ascii')
    privkeyString = privkeyBytes.decode('ascii')
    # Write both keys to the wallet file
    with open(filename, 'w') as file:
        file.write(pubkeyString)
        file.write(privkeyString)
    return

def genesis(): 
    f = open("block_0.txt", "w")
    f.write("Genesis block - Let's get started!")

    # genesis_nonce = 0

    # file = open("block_0.txt", 'r')
    # curr = ''.join(file.readlines()) + '\n'
    # # file.write('\n')
    # genesis_hash = str(hashFile("block_0.txt"))
    # while not genesis_hash.startswith("0" * 2):
    #     file = open("block_0.txt", 'w')
    #     file.write(curr)
    #     file.write("nonce: " + str(genesis_nonce))
    #     genesis_nonce += 1
    #     genesis_hash = str(hashFile("block_0.txt"))

    f.close()




    print("Genesis block created in 'block_0.txt'")
def generate(dest):
    (pubkey, privkey) = rsa.newkeys(1024)
    saveWallet(pubkey, privkey, dest)
    h = hashFile(dest)
    print("New wallet generated in", dest, "with tag", h[0:17])

def get_address(source): # WHAT IS THE HASH HERE?
    # source = sys.argv[2]
    _, _ = loadWallet(source) # Do i need to use this 
    tag = hashFile(source)
    return tag[0:17]

def fund(tag, amount, dest):
    
    # tag = sys.argv[2]
    # amount = sys.argv[3]
    # dest = sys.argv[4]

    f = open(dest, "w") 
    f.write("From: " + sourceFund + "\n")
    f.write("To: " + tag + "\n")
    f.write("Amount: " + str(amount) + "\n")
    f.write("Date: " + str(datetime.now()))
    f.close()
#------------ FIX DATETIME FORMAT -------------#
    print("Funded wallet", tag, "with", amount, NAME, "on", datetime.now() )

def transfer(source, dest, amount, filename): # python3 cmoney.py transfer alice.wallet.txt <tagb> 12 03-alice-to-bob.txt
    # source = sys.argv[2]
    # dest = sys.argv[3]
    # amount = sys.argv[4]
    # filename = sys.argv[5]

    f = open(filename, "w") 
    
    f1 = "From: " + hashFile(source)[0:17]
    f2 = "To: " + dest
    f3 = "Amount: " + amount
    f4 = "Date: " + str(datetime.now())

    f.write(f1 + "\n")
    f.write(f2 + "\n")
    f.write(f3 + "\n")
    f.write(f4 + "\n\n")

    message = (f1 + f2 + f3 + f4).encode()
    _, privkey = loadWallet(source)
    signature = rsa.sign(message, privkey, 'SHA-256')
    f.write(str(bytesToString(signature))[2:-1]) # signature trim
    # ----------- IS THE SIGNATURE CORRECT? --------------------#
    # print("signature: ", bytesToString(signature))
    f.close()

    print("Transferred " + amount + " from " + source + " to " + dest + " and the statement to " + filename +  " on " + str(datetime.now() ))
    
def balance(account_tag): #python3 cmoney.py balance <taga>
    # account_tag = sys.argv[2]
    count = 1
    balance = 0
    # check blockchain
    while True:
        filename = "block_" + str(count) + ".txt"
        if path.exists(filename) == False:
            break
        file = open(filename, 'r')
        lines = file.readlines()
            
        for line in lines:
            info = line.split(" ")
            if account_tag in line:
                if line.index("transferred") > line.index(account_tag): # money transferred from account tag
                    balance -= int(info[2])
                else:
                    balance += int(info[2])
        count += 1
    #check mempool
    file2 = open("mempool.txt", 'r')
    lines2 = file2.readlines()
    for line in lines2:
        info2 = line.split(" ")
        if account_tag in line:
            if line.index("transferred") > line.index(account_tag): # money transferred from account tag
                balance -= int(info2[2])
            else:
                balance += int(info2[2])
    return balance

def verify(wallet, transactionFilename): #python3 cmoney.py verify bob.wallet.txt 04-bob-to-alice.txt
    # wallet = sys.argv[2]
    # transactionFilename = sys.argv[3]

    pubkey, _ = loadWallet(wallet)
    file = open(transactionFilename, 'r')
    lines = file.readlines()
    message = ""
    signature = ""
    sender = lines[0][6:].strip("\n")
    reciever = lines[1][4:].strip("\n")
    amount = lines[2][8:].strip("\n")
    date = lines[3][6:].strip("\n")


    for i in range(len(lines)-2):
        message += lines[i].strip("\n")
            # print("line: ", lines[i])
    signature = lines[-1].strip("\n")
    # print(message)
    # print(signature)
    
    file.close()

    message = message.encode()
    # print(rsa.verify(message, stringToBytes(signature), pubkey))
    # print("balance: ", balance(get_address()))
    if str(sender) == sourceFund or rsa.verify(message, stringToBytes(signature), pubkey) == 'SHA-256' and balance(get_address(sys.argv[2])) >= int(amount): # is this how we check availability funds?
        file = open('mempool.txt', 'a')
        file.write(sender +  " transferred " + amount + " to " + reciever + " on " + date + "\n")
        file.close()
        print("The transaction in file " + transactionFilename + " with wallet " + wallet + " is valid, and was written to the mempool")
    else:
        print("The transaction in file " + transactionFilename + " with wallet " + wallet + " is NOT valid, and was NOT written to the mempool")

def mine(difficulty):
    # 1. calculate hash of previous block 
    

    block = ""

    #take care of block0.txt

    

   
    # #count now holds the file we are going to create
    # nonce1 = 0
    # file = open("block_" + str(count-1) + ".txt")
    # block1 = file.readline()

    
    # hashOfFile1 = str((hashFile("block_" + str(count-1) + ".txt")))
    # while not hashOfFile1.startswith("0" * int(difficulty)):
    #     file.write('\n' + "nonce: " + str(nonce1))
    #     hashOfFile1 = str((hashFile("block_" + str(count-1) + ".txt")))
    #     nonce1 += 1
    # file.close()


    count = 1


    # 2. load the transactions from mempool 
    file = open("mempool.txt", 'r')
    transactions = file.readlines()
    file.close()

    count = 1
    filename = "block_" + str(count) + ".txt"
    while path.exists(filename):
        count += 1
        filename = "block_" + str(count) + ".txt"
    
    # block += (str(bytesToString(hash))[2:-1])
    # block += genesis_hash
    # if not path.exists("block_1.txt"):
    print("COUNT: ", count)
    block += str(hashFile("block_" + str(count-1)+".txt"))
    block += '\n\n'

    for transaction in transactions: 
        block += transaction
    block += '\n'
    # 3. clear the mempool
    open('mempool.txt', 'w').close() # clear the mempool

    # 4. find appropriate nonce

    blockwrite = block + "nonce: "
    hash = ""
    nonce = -1

    while not hash.startswith("0" * int(difficulty)):
        nonce += 1
        h = hashlib.sha256()
        h.update((blockwrite + str(nonce)).encode())
        hash = h.hexdigest()
    
    with open("block_" + str(count) + ".txt", 'w') as f:
        f.write(blockwrite + str(nonce))

    # nonce = 0
    # blockwrite = block + "nonce: " + str(nonce)
    # file = open("block_" + str(count) + ".txt", 'w')
    # file.write(blockwrite)
    # file.close()
    # hashOfFile = str((hashFile("block_" + str(count) + ".txt")))
    # nonce += 1
    # while not hashOfFile.startswith("0" * int(difficulty)):
    #     file = open("block_" + str(count) + ".txt", 'w')
        
        
    #     # if str(hashFile("block_" + str(count) + ".txt"))[0:int(difficulty)] == "0" * int(difficulty):
    #         # break
        
        
    #     blockwrite = block + "nonce: " + str(nonce)
    #     # print(hashOfFile)
    #     file.write(blockwrite)
    #     hashOfFile = str((hashFile("block_" + str(count) + ".txt")))
    #     # print(hashOfFile)
    #     nonce += 1
    # file.close()
    print("Mempool transactions moved to block_" + str(count) + ".txt and mined with difficulty", str(difficulty), "and nonce", str(nonce-1))

def validate():
    # res = True
    count = 1
    while True:
        filename = "block_" + str(count) + ".txt"
        
        if path.exists(filename) == False:
            # file.close()
            return True
        file = open(filename, 'r')
        previous = str(hashFile("block_" + str(count-1) + ".txt"))
        hash = file.readlines()[0]
        if hash.strip() != previous.strip():
            file.close()
            # print("hash: ", hash)
            # print("previous: ", previous)
            # print(type(hash), type(previous))
            return False
        count += 1

    # return False

match sys.argv[1]:
    # 1. Print name of currency
    case "name":
        print(NAME)
    # 2. Create the genesis block 
    case "genesis":
        genesis()
    # 3. Generate a wallet. This will create RSA public/private key set 
    case "generate":
        generate(sys.argv[2])
    case "address":
        print(get_address(sys.argv[2]))
    case "fund":
        fund(sys.argv[2], sys.argv[3], sys.argv[4])
    case "transfer":
        transfer(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    case "balance":
        print(balance(sys.argv[2]))
    case "verify":
        verify(sys.argv[2], sys.argv[3])
    case "mine":
        mine(sys.argv[2])
    case "validate":
        print(validate())