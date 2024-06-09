import json
import time

from web3 import Web3


def check_transfers(from_address, to_address, token_address, sepolia_url="https://sepolia-rpc.tokensoft.io"):
    web3 = Web3(Web3.HTTPProvider(sepolia_url))

    if not web3.isConnected():
        print("Не удалось подключиться к сети Sepolia")
        return None

    with open("src/token_abi.json", "r") as abi_file:
        erc20_abi = json.load(abi_file)

    contract = web3.eth.contract(address=token_address, abi=erc20_abi)

    start_time = int(time.time()) - 300

    def get_transfers():
        latest_block = web3.eth.get_block("latest")
        start_block = latest_block["number"] - 50

        transfers = []
        for block_num in range(start_block, latest_block["number"] + 1):
            block = web3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                if tx["to"] and tx["to"].lower() == token_address.lower():
                    try:
                        decoded_input = contract.decode_function_input(tx.input)
                        if (
                            decoded_input[0].fn_name == "transfer"
                            and decoded_input[1]["_to"].lower() == to_address.lower()
                            and tx["from"].lower() == from_address.lower()
                        ):
                            if block.timestamp >= start_time:
                                transfers.append(decoded_input[1]["_value"])
                    except Exception as e:
                        continue

        return transfers

    transfers = get_transfers()
    if transfers:
        total_amount = sum(transfers)
        return total_amount
    else:
        return 0
