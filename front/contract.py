import json

from web3 import Web3


class ContractInteraction:
    def __init__(self, account_address, private_key, contract_address, sepolia_url="https://sepolia-rpc.tokensoft.io"):
        self.account_address = account_address
        self.private_key = private_key
        self.contract_address = contract_address

        self.w3 = Web3(Web3.HTTPProvider(sepolia_url))

        with open("src/contract_abi.json", "r") as abi_file:
            self.contract_abi = json.load(abi_file)

        self.contract = self.w3.eth.contract(address=contract_address, abi=self.contract_abi)

    def send_transaction(self, function_name, function_args):
        nonce = self.w3.eth.getTransactionCount(self.account_address)

        txn_dict = self.contract.functions.__getattr__(function_name)(*function_args).buildTransaction(
            {
                "chainId": 69,  # Sepolia chain ID
                "gas": 1000000,
                "gasPrice": self.w3.toWei("50", "gwei"),
                "nonce": nonce,
            }
        )

        signed_txn = self.w3.eth.account.signTransaction(txn_dict, self.private_key)

        txn_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        receipt = self.w3.eth.waitForTransactionReceipt(txn_hash)

        return receipt

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
        return self.contract.functions.deals(deal_id).call()


# Example usage
# contract_interaction = ContractInteraction(
#     '0xYourAddress',
#     'YourPrivateKey',
#     '0xContractAddress'
# )

# contract_interaction.createDeal('123', '0xclientaddress', '0ximplementeraddress', '0xtokenaddress', 100)
# contract_interaction.completeDeal('123')
# contract_interaction.denyDeal('123')
# contract_interaction.depositTokens('123')
# contract_interaction.finalizeDeal('123', 80)
# deal_info = contract_interaction.getDealInfo('123')
