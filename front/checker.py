import json
import requests
import time

async def check_transfers(api_key, from_address, to_address, token_address):
    url = f"https://api-sepolia.etherscan.io/api?module=account&action=tokentx&address={from_address}&contractaddress={token_address}&startblock=0&endblock=999999999&sort=asc&apikey={api_key}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch token transfers: {response.status_code}")

    data = response.json()
    if data.get("status") != "1":
        return 0

    transfers = []
    for tx in data.get("result", []):
        if tx["to"].lower() == to_address.lower():
            timestamp = int(tx["timeStamp"])
            if timestamp >= (time.time() - 300):  # Within the last 5 minutes
                transfers.append(int(tx["value"]))

    if transfers:
        total_amount = sum(transfers)
        return total_amount / 10 ** 18
    else:
        return 0