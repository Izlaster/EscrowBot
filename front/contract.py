import json
from web3 import Web3

class ContractInteraction:
    def __init__(self, account_address, private_key, contract_address, sepolia_url):
        self.account_address = account_address
        self.private_key = private_key
        self.contract_address = contract_address

        self.w3 = Web3(Web3.HTTPProvider(sepolia_url))

        with open("src/contract_abi.json", "r") as abi_file:
            self.contract_abi = json.load(abi_file)

        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

    def send_transaction(self, function_name, function_args):
        try:
            nonce = self.w3.eth.get_transaction_count(self.account_address)
            contract_function = getattr(self.contract.functions, function_name)

            if not contract_function:
                print(f"Function {function_name} does not exist in the contract.")
                return None

            if not isinstance(function_args, (list, tuple)):
                print(f"Function arguments must be a list or tuple. Got {type(function_args)}")
                return None

            # Increase the gas price to ensure the transaction is not underpriced
            gas_price = self.w3.to_wei('50', 'gwei')  # Increase the gas price
            gas_limit = 500000  # Set an appropriate gas limit

            transaction = contract_function(*function_args).build_transaction(
                {
                    'nonce': nonce,
                    'chainId': 11155111,
                    'from': self.account_address,
                    'gas': gas_limit,
                    'gasPrice': gas_price
                }
            )

            signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction).hex()
            print(f"Transaction hash: {tx_hash}")

            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt['status'] == 1:
                print("Transaction successful")
            else:
                print("Transaction failed")

            return tx_hash

        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"Function name: {function_name}")
            print(f"Function arguments: {function_args}")
            print(f"Transaction: {transaction if 'transaction' in locals() else 'Transaction not created'}")
            return None

    def createDeal(self, deal_id, client, implementer, token, transaction_amount):
        return self.send_transaction("createDeal", [deal_id, client, implementer, token, transaction_amount])

    def completeDeal(self, deal_id):
        return self.send_transaction("completeDeal", [deal_id])

    def denyDeal(self, deal_id):
        return self.send_transaction("denyDeal", [deal_id])

    def depositTokens(self, deal_id):
        return self.send_transaction("depositTokens", [deal_id])

    def finalizeDeal(self, deal_id, implementer_percentage):
        return self.send_transaction("finalizeDeal", [deal_id, implementer_percentage])

    def getDealInfo(self, deal_id):
        try:
            return self.contract.functions.deals(deal_id).call()
        except Exception as e:
            print(f"An error occurred while retrieving deal info: {e}")
            return None