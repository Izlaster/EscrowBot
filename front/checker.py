import time
from web3 import Web3

def check_transactions(sepolia_rpc_url, from_address, our_address):
    web3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))
    latest_block = web3.eth.get_block('latest')
    latest_block_number = latest_block['number']

    # Получение времени текущего блока
    latest_block_time = latest_block['timestamp']

    # Перемотка на 5 минут назад (300 секунд)
    start_time = latest_block_time - 300

    print(f'Checking transactions from block {latest_block_number} and earlier (last 5 minutes)')

    block = latest_block
    while block['timestamp'] >= start_time:
        block_number = block['number']
        print(f'Checking block {block_number} at timestamp {block["timestamp"]}')
        
        for tx_hash in block['transactions']:
            tx = web3.eth.get_transaction(tx_hash)
            if tx['from'].lower() == from_address.lower() and tx['to'].lower() == our_address.lower():
                print(f'Found transaction from {from_address} to {our_address}:')
                print(f'  Transaction hash: {tx_hash}')
                print(f'  Value: {web3.fromWei(tx["value"], "ether")} Ether')
                print(f'  Timestamp: {block["timestamp"]}')

        if block_number == 0:
            break
        block = web3.eth.get_block(block_number - 1)
