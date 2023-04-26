from web3 import Web3
from hexbytes import HexBytes
import math
from web3.middleware import geth_poa_middleware

import arbitrage_config

config = arbitrage_config.config

abi = arbitrage_config.idex_abi


# my_address = '0x8c78e7ed4e60a4cd6bf8691c579839f272478ab9'
# private_key = HexBytes('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')

account_address = config['account_address']
account_private_key = config['account_private_key']
connection_is_ipc = config['connection_is_ipc']
connection_uri = config['connection_uri']
price_eth = config['price_eth']
price_tc = config['price_tc']
dex_addrs = config['dex_addrs']
tokencc_addr = config['tokencc_addr']
max_eth_to_trade = config['max_eth_to_trade']
max_tc_to_trade = config['max_tc_to_trade']
gas_price = config['gas_price']
dex_fees = config['dex_fees']

def setup_w3():
    if connection_is_ipc:
        w3 = Web3(Web3.IPCProvider(connection_uri))
    else:
        w3 = Web3(Web3.WebsocketProvider('wss://andromeda.cs.virginia.edu/geth'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # print(w3.is_connected())
    # print(w3.eth.get_block('latest'))
    return w3

def get_contract(w3, address, abi_spec):
    # print("dex_addr: ", address)
    contract = w3.eth.contract(address=address, abi=abi_spec)
    return contract

def getF(contract):
    feeNumerator = contract.functions.feeNumerator().call()
    feeDenominator = contract.functions.feeDenominator().call()
    return 1 - feeNumerator/feeDenominator

def getXYK(contract, token_contract):
    x = contract.functions.x().call()
    y = contract.functions.y().call()
    k = contract.functions.k().call()
    return x / (10 ** 18), y / (10 ** token_contract.functions.decimals().call()), k / (10 ** (18 + token_contract.functions.decimals().call()))

def getBalance(contract, addr):
    balance = contract.functions.balanceOf(addr).call()
    return balance

def holdings_now(q_e, q_t, p_e, p_t):
    return q_e * p_e + q_t * p_t

def delta_t(y_d, f, k_d, p_e, p_t):
    return y_d * (-1) + math.sqrt(f * k_d * p_e/p_t)

def delta_e(x_d, f, k_d, p_e, p_t):
    return x_d * (-1) + math.sqrt(f * k_d * p_t/p_e)


def holdings_after_ETH2(q_t, f, y_d, k_d, x_d, delta_ETH):
    # print(((q_t + f * y_d - f * (k_d / (x_d + delta_ETH))) - q_t))
    return ((q_t + f * y_d - f * (k_d / (x_d + delta_ETH))) - q_t)


def holdings_after_ETH(q_e, f, x_d, k_d, y_d, delta_t, p_e, q_t, p_t, g):
    h_after = (q_e + f * x_d - f * k_d/(y_d + delta_t)) * p_e + (q_t-delta_t) * p_t - g * p_e
    # print("boom", h_after)
    return h_after

def holdings_after_TC2(q_e, f, y_d, k_d, x_d, d_t):
    return ((q_e + f * x_d - f * (k_d / (y_d + d_t))) - q_e)

def holdings_after_TC(q_t, f, y_d, k_d, x_d, delta_e, p_t, q_e, p_e, g):
    h_after = (q_t + f * y_d - f * k_d / (x_d + delta_e)) * p_t + (q_e - delta_e) * p_e - g * p_e 
    return h_after

def gas_estimate(w3, transaction):
    gas = w3.eth.estimate_gas(transaction)
    return gas

def checksum_addr(addr):
    return Web3.to_checksum_address(addr)




def create_Transaction_transfer(w3, contract, my_address, dex_addr, amount):
    # print(amount)
    # amount = max(amount, max_tc_to_trade)
    transaction = contract.functions.transfer(dex_addr, amount).build_transaction({
    'gas': 2100000,
    'chainId': 67834503,
    'gasPrice': w3.to_wei(gas_price, 'gwei'),
    'from': my_address,
    'nonce': w3.eth.get_transaction_count(my_address)
    })
    return transaction

def create_Transaction(w3, my_address, dex_address, amount):
    # print(w3.eth.get_balance(my_address))
    transaction = {
    'chainId': 67834503,
    'nonce': w3.eth.get_transaction_count(my_address),
    'from': my_address,
    'to': dex_address,
    'value': w3.to_wei(amount, 'ether'),
    'gas': 2100000,
    'gasPrice': Web3.to_wei(gas_price, 'gwei')
    }
    return transaction


# gwei_fees = gas * gas_price
#         wei_fees = w3.to_wei(gwei_fees, 'gwei')
#         gas_fees = float (w3.from_wei(wei_fees, 'ether')) # g

def etherToGwei(w3, amount): # 92.1883209278185
    wei =  w3.to_wei(amount, 'ether')
    gwei = w3.from_wei(wei, 'gwei')
    return gwei


def setQE(w3):
    return w3.eth.get_balance(account_address) / (10 ** 18)

def setQT(token_contract):
    return getBalance(token_contract, account_address) / (10 ** token_contract.functions.decimals().call())


# tcAmount = (q_t + (f * y) - (f*(k/(x+d_e))))





def main():
    w3 = setup_w3()

    # output numbers
    
    fees = 0
    maxHolding = 0
    ethAmount = 0
    tcAmount = 0
    transactionFinal = None

    

    h_now = holdings_now(max_eth_to_trade, max_tc_to_trade, price_eth, price_tc)
    maxHolding = h_now # can never be lower than h_now

    token_contract = get_contract(w3, tokencc_addr, arbitrage_config.itokencc_abi)
    q_e,q_t = setQE(w3), setQT(token_contract)

    for dex_addr in dex_addrs:
        
        # fees = 0
        contract = get_contract(w3, dex_addr, abi)
        f = getF(contract)
        
        decimals = token_contract.functions.decimals().call()
        x,y,k = getXYK(contract, token_contract)

        d_t = delta_t(y, f, k, price_eth, price_tc)
        d_e = delta_e(x, f, k, price_eth, price_tc)

        checksum_my_address = checksum_addr(account_address)

        


        balance = getBalance(token_contract, account_address)
        d_t = min(balance, d_t)
        d_t = min(max_tc_to_trade, d_t) # don't go above max

        if d_t > 0:
            # print("d_t: ", d_t)
            transaction_TC = create_Transaction_transfer(w3, token_contract, checksum_my_address, dex_addr, int(d_t * 10 ** decimals))

            gas = gas_estimate(w3, transaction_TC)
            gwei_fees = gas * gas_price
            wei_fees = w3.to_wei(gwei_fees, 'gwei')
            gas_fees = float (w3.from_wei(wei_fees, 'ether')) # g
            gas_fees_USD = gas_fees * price_eth 
            h_after_ETH = holdings_after_ETH(q_e, f, x, k, y, d_t, price_eth, q_t, price_tc, gas_fees)
            # h_after_ETH = holdings_after_ETH2(max_tc_to_trade, f, y, k, x, d_e)

            
            if h_after_ETH > maxHolding:
                maxHolding = max(maxHolding, h_after_ETH)
                # ethAmount = d_t * x / y - gas_fees_USD
                ethAmount = holdings_after_TC2(q_e, f, y, k, x, d_t) # CHANGED HERE
                fees = (ethAmount * price_eth * dex_fees + gas_fees_USD)
                # print("FEESNOW: ", fees)
                ethAmount *= (1-dex_fees) 
                tcAmount = d_t * (-1) 
                # tcAmount = d_t * (-1)
                # tcAmount = holdings_after_ETH2(max_tc_to_trade, f, y, k, x, d_e)
                # print("dex fees: ", dex_fees)
                # print("gas_fees: ", gas_fees)

                
                transactionFinal = transaction_TC
        balance_eth = w3.eth.get_balance(account_address)
        d_e = min(d_e, balance_eth)
        d_e = min(d_e, max_eth_to_trade)

        if d_e > 0:
            transaction_ETH = create_Transaction(w3, checksum_my_address, dex_addr, d_e) # what units is this in

            gas = gas_estimate(w3, transaction_ETH)
            gwei_fees = gas * gas_price
            wei_fees = w3.to_wei(gwei_fees, 'gwei')
            gas_fees = float (w3.from_wei(wei_fees, 'ether')) # g
            gas_fees_USD = gas_fees * price_eth

            h_after_TC = holdings_after_TC(q_t, f, y, k, x, d_e, price_tc, q_e, price_eth, gas_fees)
            if h_after_TC > maxHolding:
                maxHolding = max(maxHolding, h_after_TC)
                # tcAmount = d_e * y/x - gas_fees_USD
                tcAmount = holdings_after_ETH2(q_t, f, y, k, x, d_e) #  CHANGED HERE 
                # tcAmount = (max_tc_to_trade + f * y - f * (k / (x + d_e))) - max_tc_to_trade
                # tcAmount = 
                # print("tcAmount15: ", tcAmount)

                fees = (tcAmount * price_tc * dex_fees + gas_fees_USD)
                
                tcAmount *= (1-dex_fees)
                ethAmount = d_e * (-1)

                # print(ethAmount)
                # print("dex fees: ", dex_fees)
                # print("gas_fees: ", gas_fees)
                
                transactionFinal = transaction_ETH
        
        # print("Fee value (f): ", f)
        # print("x,y,k from DEX: ", x, y,k)
        # print("holdings now (h_now): ", h_now)
        # print("delta_t: ", d_t)
        # print("delta_e:", d_e)
        # print("gas fees (USD): ", gas_fees_USD)
        # print("total fees:", fees)
        # print("gas fees (TC withheld): ", gas_fees * price_tc)
        # print("gas fees (ETH withheld): ", gas_fees * price_eth)
        
        # if d_t > 0:
        #     print("dex_fees: ", (d_t * x/y * price_eth - gas_fees) * dex_fees)
        #     print("holdings_after_ETH: ", h_after_ETH)
        # if d_e > 0:
        #     print("dex_fees: ", (d_e * y/x * price_tc - gas_fees) * dex_fees)
        #     print("holdings_after_TC:", h_after_TC)
        # print("ethAmount: ", ethAmount)
        # print("tcAmount: ", tcAmount)
        # print("\n")
    
    if ethAmount != 0 and tcAmount != 0:
        signed_txn = w3.eth.account.sign_transaction(transactionFinal, private_key=account_private_key)
        ret = w3.eth.send_raw_transaction(signed_txn.rawTransaction)


        q_e += ethAmount
        q_t += tcAmount

        w3.eth.wait_for_transaction_receipt(ret)

        # print(w3.eth.get_transaction(ret))
    # print("tcamount: ", tcAmount)
    # print("q_e: ", q_e)
    # print("q_t:" , q_t)
    arbitrage_config.output(ethAmount, tcAmount, fees, maxHolding)


        

    # print(abi)

if __name__ == "__main__":
    main()
