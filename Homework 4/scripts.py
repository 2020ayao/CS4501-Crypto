#!/usr/bin/python3

# This is the homework submission file for the BTC Scripting homework, which
# can be found at http://aaronbloomfield.github.io/ccc/hws/btcscript.  That
# page describes how to fill in this program.


from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin import SelectParams
from bitcoin.core import CMutableTransaction
from bitcoin.core.script import *
from bitcoin.core import x


#------------------------------------------------------------
# Do not touch: change nothing in this section!

# ensure we are using the bitcoin testnet and not the real bitcoin network
SelectParams('testnet')

# The address that we will pay our tBTC to -- do not change this!
tbtc_return_address = CBitcoinAddress('mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB') # https://coinfaucet.eu/en/btc-testnet/

# The address that we will pay our BCY to -- do not change this!
bcy_dest_address = CBitcoinAddress('mgBT4ViPjTTcbnLn9SFKBRfGtBGsmaqsZz')

# Yes, we want to broadcast transactions
broadcast_transactions = True

# Ensure we don't call this directly
if __name__ == '__main__':
    print("This script is not meant to be called directly -- call bitcoinctl.py instead")
    exit()


#------------------------------------------------------------
# Setup: your information

# Your UVA userid
userid = 'aly3ye'

# Enter the BTC private key and invoice address from the setup 'Testnet Setup'
# section of the assignment.  
my_private_key_str = "cSD3PkXAxnTtmuZzsteECzABsJAPDWwV7WxexHgVt3dUKyjRk4uz"
my_invoice_address_str = "mrfpiWovx1gThFoTqaBaqk2B4iWXLCrnQC"

# Enter the transaction ids (TXID) from the funding part of the 'Testnet
# Setup' section of the assignment.  Each of these was provided from a faucet
# call.  And obviously replace the empty string in the list with the first
# one you obtain..
txid_funding_list = ["b93b241b73f5daac3781d10b111505588a5f1975dffbcbdad0ce576e9574a66f"]

# These conversions are so that you can use them more easily in the functions
# below -- don't change these two lines.
if my_private_key_str != "":
    my_private_key = CBitcoinSecret(my_private_key_str)
    my_public_key = my_private_key.pub


#------------------------------------------------------------
# Utility function(s)

# This function will create a signature of a given transaction.  The
# transaction itself is passed in via the first three parameters, and the key
# to sign it with is the last parameter.  The parameters are:
# - txin: the transaction input of the transaction being signed; type: CMutableTxIn
# - txout: the transaction output of the transaction being signed; type: CMutableTxOut
# - txin_scriptPubKey: the pubKey script of the transaction being signed; type: list
# - private_key: the private key to sign the transaction; type: CBitcoinSecret
def create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, private_key):
    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx, 0, SIGHASH_ALL)
    return private_key.sign(sighash) + bytes([SIGHASH_ALL])


#------------------------------------------------------------
# Testnet Setup: splitting coins

# The transaction ID that is to be split -- the assumption is that it is the
# transaction hash, above, that funded your account with tBTC.  You may have
# to split multiple UTXOs, so if you are splitting a different faucet
# transaction, then change this appropriately. It must have been paid to the
# address that corresponds to the private key above
txid_split = txid_funding_list[0]

# After all the splits, you should have around 10 (or more) UTXOs, all for the
# amount specified in this variable. That amount should not be less than
# 0.0001 BTC, and can be greater.  It will make your life easier if each
# amount is a negative power of 10, but that's not required.
# split_amount_to_split = 0.01077763
# split_amount_to_split = 0.01431473
split_amount_to_split = 0.001


# How much BTC is in that UTXO; look this up on https://live.blockcypher.com
# to get the correct amount.
# split_amount_after_split = 0.001
split_amount_after_split = 0.0001

# How many UTXO indices to split it into -- you should not have to change
# this!  Note that it will actually split into one less, and use the last one
# as the transaction fee.
split_into_n = int(split_amount_to_split/split_amount_after_split)

# The transaction IDs obtained after successfully splitting the tBTC.
txid_split_list = ["6dc308d377cbb2487189676e44444beb31fce8c324064f8055a5b83f6192be08"]
# txid_split_list = ["5a6e69ed40592a13ad4effbf8cc7644ff0dc8691697c88809c20e54a78093278"]

#------------------------------------------------------------
# Global settings: some of these will need to be changed for EACH RUN

# The transaction ID that is being redeemed for the various parts herein --
# this should be the result of the split transaction, above; thus, the
# default is probably sufficient.
txid_utxo = txid_split_list[0]

# This is likely not needed.  The bitcoinctl.py will take a second
# command-line parmaeter, which will override this value.  You should use the
# second command-line parameter rather than this variable. The index of the
# UTXO that is being spent -- note that these indices are indexed from 0.
# Note that you will have to change this for EACH run, as once a UTXO index
# is spent, it can't be spent again.  If there is only one index, then this
# should be set to 0.
utxo_index = -1

# How much tBTC to send -- this should be LESS THAN the amount in that
# particular UTXO index -- if it's not less than the amount in the UTXO, then
# there is no miner fee, and it will not be mined into a block.  Setting it
# to 90% of the value of the UTXO index is reasonable.  Note that the amount
# in a UTXO index is split_amount_to_split / split_into_n.
send_amount = split_amount_after_split * 0.9


#------------------------------------------------------------
# Part 1: P2PKH transaction

# This defines the pubkey script (aka output script) for the transaction you
# are creating.  This should be a standard P2PKH script.  The parameter is:
# - address: the address this transaction is being paid to; type:
#   P2PKHBitcoinAddress
def P2PKH_scriptPubKey(address):
    return [ 
            OP_DUP,
            OP_HASH160,
            address, 
            OP_EQUALVERIFY,
            OP_CHECKSIG
           ]

# This function provides the sigscript (aka input script) for the transaction
# that is being redeemed.  This is for a standard P2PKH script.  The
# parameters are:
# - txin: the transaction input of the UTXO being redeemed; type:
#   CMutableTxIn
# - txout: the transaction output of the UTXO being redeemed; type:
#   CMutableTxOut
# - txin_scriptPubKey: the pubKey script (aka output script) of the UTXO being
#   redeemed; type: list
# - private_key: the private key of the redeemer of the UTXO; type:
#   CBitcoinSecret
def P2PKH_scriptSig(txin, txout, txin_scriptPubKey, private_key):
    # print("txin: ", txin)
    # print("txout: " txout)
    # print("txin_scriptPubKey: ", txin_scriptPubKey)
    # print("private_key: ", private_key)

    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx, 0, SIGHASH_ALL)
    sig = private_key.sign(sighash) + bytes([SIGHASH_ALL])

    priv_key = CBitcoinSecret(str(private_key))
    public_key = priv_key.pub


    return [ 
             sig, 
             public_key
           ]

# The transaction hash received after the successful execution of this part
txid_p2pkh = "640fc2e2d01af0d87bac70fd17c7792bda176296b144b211530f62c0142f5e08"


#------------------------------------------------------------
# Part 2: puzzle transaction

# These two values are constants that you should choose -- they should be four
# digits long.  They need to allow for only integer solutions to the linear
# equations specified in the assignment.
puzzle_txn_p = 4231
puzzle_txn_q = 6953

# These are the solutions to the linear equations specified in the homework
# assignment.  You can use an online linear equation solver to find the
# solutions.
puzzle_txn_x = 1509
puzzle_txn_y = 2722

# This function provides the pubKey script (aka output script) that requres a
# solution to the above equations to redeem this UTXO.
def puzzle_scriptPubKey():
    return [ 
                OP_2DUP,
                OP_ADD,
                puzzle_txn_p,
                OP_EQUALVERIFY,
                OP_DUP,
                OP_ADD,
                OP_ADD,
                puzzle_txn_q,
                OP_EQUAL
           ]

# This function provides the sigscript (aka input script) for the transaction
# that you are redeeming.  It should only provide the two values x and y, but
# in the order of your choice.
def puzzle_scriptSig():
    return [ 
             puzzle_txn_x,
             puzzle_txn_y
           ]

# The transaction hash received after successfully submitting the first
# transaction above (part 2a)
txid_puzzle_txn1 = "9e304c0ba6570a84775fdc1a34bf15f6f5c56464ef673e5f806c67e1c7999f30"

# The transaction hash received after successfully submitting the second
# transaction above (part 2b)
txid_puzzle_txn2 = "14d7eff48252c6a18d0c23dc6cf9d16d8bfb5a484156ac941f24f4c4ba30a1e5"


#------------------------------------------------------------
# Part 3: Multi-signature transaction

# These are the public and private keys that need to be created for alice,
# bob, and charlie
alice_private_key_str = "cT9KD8WJGmRqpFQ2mhvv7ZjeWXp4D3YNx4bEohFXmxeepL63WP9V"
alice_invoice_address_str = "n4cDyydKfbziiZTV7g8twRGQSULdGRumob"
bob_private_key_str = "cNrFbrk7RuSYAwFCaXDL5KmJdTLCMv2GkKUqFCj87qmeroXK1Vx9"
bob_invoice_address_str = "msb7kQUgCuQVuvy5FUSj5kBMTibjLwnQ9a"
charlie_private_key_str = "cVPMnRzZ3pHMqhAazgY4ZBYbSS3qBLYCFTD5Fhu5gxXem43pTekZ"
charlie_invoice_address_str = "n4cjVnnEmKekTLJimQhVLhat1vgLGZMqFC"

# These three lines convert the above strings into the type that is usable in
# a script -- you should NOT modify these lines.
if alice_private_key_str != "":
    alice_private_key = CBitcoinSecret(alice_private_key_str)
if bob_private_key_str != "":
    bob_private_key = CBitcoinSecret(bob_private_key_str)
if charlie_private_key_str != "":
    charlie_private_key = CBitcoinSecret(charlie_private_key_str)

# This function provides the pubKey script (aka output script) that will
# require multiple different keys to allow redeeming this UTXO.  It MUST use
# the OP_CHECKMULTISIGVERIFY opcode.  While there are no parameters to the
# function, you should use the keys above for alice, bob, and charlie, as
# well as your own key.
def multisig_scriptPubKey():
    return [
            # OP_DUP,
            # OP_HASH160,
            # my_invoice_address_bcy_str, 
            # OP_EQUALVERIFY,
            # OP_CHECKSIGVERIFY,
            my_private_key.pub,
            OP_CHECKSIGVERIFY,
            alice_private_key.pub,
            bob_private_key.pub,
            charlie_private_key.pub,
            OP_3,
            OP_CHECKMULTISIGVERIFY,
            OP_1            
           ]

# This function provides the sigScript (aka input script) that can redeem the
# above transaction.  The parameters are the same as for P2PKH_scriptSig
# (), above.  You also will need to use the keys for alice, bob, and charlie,
# as well as your own key.  The private key parameter used is the global
# my_private_key.
def multisig_scriptSig(txin, txout, txin_scriptPubKey):
    bank_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, my_private_key)
    alice_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, alice_private_key)
    bob_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, bob_private_key)
    charlie_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, charlie_private_key)
    


    # tx = CMutableTransaction([txin], [txout])
    # sighash = SignatureHash(CScript(txin_scriptPubKey), tx, 0, SIGHASH_ALL)
    # sig = my_private_key.sign(sighash) + bytes([SIGHASH_ALL])
    return [ 
            OP_0, 
            alice_sig, 
            bob_sig,
            OP_2, 
            bank_sig
           ]

# The transaction hash received after successfully submitting the first
# transaction above (part 3a)
txid_multisig_txn1 = "0847db52dc61c2ba1bc937dde44d55fdd133424926a8187547dd466aa00ed536"

# The transaction hash received after successfully submitting the second
# transaction above (part 3b)
txid_multisig_txn2 = "ca9f5b62753cc3be4e51cdf4ae941f6b336a50b579473b2d26531f8506c4ae32"


#------------------------------------------------------------
# Part 4: cross-chain transaction

# This is the API token obtained after creating an account on
# https://accounts.blockcypher.com/.  This is optional!  But you may want to
# keep it here so that everything is all in once place.
blockcypher_api_token = "44804a9f95644b9c87035afa2bb26c0e"

# These are the private keys and invoice addresses obtained on the BCY test
# network.
my_private_key_bcy_str = "bedf5ef48ade725226a935a9e6681f2dd6604a0568d4b2e1a804478ced661965"
my_public_key_bcy_str = "024b0b7dc335e2ccc704320c3db0f496fa3ce9dc4aa53f61b01567c395b3357cfe"
my_invoice_address_bcy_str = "C66LaEG2eMYd1DJachLpqm1h3rig5cg1Vq"
my_wif_bcy_str = "Buj4Z1ZVSMafTNiX3jEXwsZEa18KGtcWoqdD1ZrmWjzZqo8o1BY4"

bob_private_key_bcy_str = "ab1ed9adcc37e922459054f17f2f9fcdd4b4835643b4c193d1a47aa1ef572665"
bob_public_key_bcy_str = "03b070363335c39867060fd56a9e5b949601742780fe91211bc01c277a27f3f3e6"
bob_invoice_address_bcy_str = "CGMP4jLG74hotRxpHbHAH9RFkgU7NyZ9yx"
bob_wif_bcy_str = "Bu4fcygPSam8AYJErYrbzvH9UGEnKTwGwPxs4XppJmdAXoqGvDLY"

# This is the transaction hash for the funding transaction for Bob's BCY
# network wallet.
txid_bob_bcy_funding = "cf93df9a1624943b03630b983985551b3c7fb1510b6b06d5ee040ff175f586c4"

# This is the transaction hash for the split transaction for the trasnaction
# above.
txid_bob_bcy_split = "6bd186c723c4c02eafd641ed80605a43360d3cfe2aab143e69441a04fd160330"

# This is the secret used in this atomic swap.  It needs to be between 1 million
# and 2 billion.
atomic_swap_secret = 1566038372

# This function provides the pubKey script (aka output script) that will set
# up the atomic swap.  This function is run by both Alice (aka you) and Bob,
# but on different networks (tBTC for you/Alice, and BCY for Bob).  This is
# used to create TXNs 1 and 3, which are described at
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/xchainpt1.
def atomicswap_scriptPubKey(public_key_sender, public_key_recipient, hash_of_secret):
    return [ 
            OP_IF,
            OP_HASH160,
            hash_of_secret,
            OP_EQUALVERIFY,
            public_key_recipient,
            OP_CHECKSIG,

            OP_ELSE,
            public_key_sender,
            OP_CHECKSIGVERIFY,
            public_key_recipient,
            OP_CHECKSIG,
            OP_ENDIF
           ]

# This is the ScriptSig that the receiver will use to redeem coins.  It's
# provided in full so that you can write the atomicswap_scriptPubKey()
# function, above.  This creates the "normal" redeeming script, shown in steps 5 and 6 at 
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/atomicsteps.
def atomcswap_scriptSig_redeem(sig_recipient, secret):
    return [
        sig_recipient, secret, OP_TRUE,
    ]

# This is the ScriptSig for sending coins back to the sender if unredeemed; it
# is provided in full so that you can write the atomicswap_scriptPubKey()
# function, above.  This is used to create TXNs 2 and 4, which are
# described at
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/xchainpt1.  In
# practice, this would be time-locked in the future -- it would include a
# timestamp and call OP_CHECKLOCKTIMEVERIFY.  Because the time can not be
# known when the assignment is written, and as it will vary for each student,
# that part is omitted.
def atomcswap_scriptSig_refund(sig_sender, sig_recipient):
    return [
        sig_recipient, sig_sender, OP_FALSE,
    ]

# The transaction hash received after successfully submitting part 4a
txid_atomicswap_alice_send_tbtc = "1929ae6d45656249a32d247619fe7b0deab8e1e33f7483f28d6884eef9cfe5d2" # round1 
# txid_atomicswap_alice_send_tbtc = "cb5eccc538424c63c3ec9f65f7733fab518922c5445ed70fd9096febdee9929f" # round2

# The transaction hash received after successfully submitting part 4b
txid_atomicswap_bob_send_bcy = "c55293afcc7d168caa99bf18fcfd6f467145e0946ae4c762966578502f8dcdd7" # round1 
# txid_atomicswap_bob_send_bcy = "fc723cfe95df8b530ae73acc2ddd066a475c1d96d9d969f3a6fea9f21dc6e3c3" # round2

# The transaction hash received after successfully submitting part 4c
txid_atomicswap_alice_redeem_bcy = "b013f406ba26dde26e0bd39fa23206e79f6a7d2f9ca89088b1bf855d1347d1f1" # round1 
# txid_atomicswap_alice_redeem_bcy = "9e5db35132c69887a20ef8c6e2ded884f6d9054629406ccb0d0ed7d5fccd8fbc" # round2

# The transaction hash received after successfully submitting part 4d
txid_atomicswap_bob_redeem_tbtc = "225c99a47f5068527b5b324d0c48c07875f59e3cfb52ac520f847b07413e4e88" # round1 
# txid_atomicswap_bob_redeem_tbtc = "c2881b6f50f7a866cc77f24bb64857745d1561137b576b9f2ca2eb4f6cb3e710" #round2

# txid_atomicswap_bob_redeem_tbtc = "63b98482ee556755c3f2cb5c10fc82707a7c6056b6913c59a142bee76bc60055"

#------------------------------------------------------------
# part 5: return everything to the faucet

# nothing to fill in here, as we are going to look at the balance of
# `my_invoice_address_str` to verify that you've completed this part.
