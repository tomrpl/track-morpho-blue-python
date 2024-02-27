# main.py

import asyncio
import json
from decouple import config
from web3 import Web3
from src import fetcher, markets
from decimal import Decimal, getcontext

getcontext().prec = 18

async def main():
    RPC_URL = config('RPC_URL')
    contract_address = '0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
    user_address = "0x9CBF099ff424979439dFBa03F00B5961784c06ce"

    with open('./abis/MorphoBlue.json') as f:
        morphoblue_abi = json.load(f)
    provider = Web3(Web3.HTTPProvider(RPC_URL))

    morphoblue_contract = provider.eth.contract(address=contract_address, abi=morphoblue_abi)
    tasks = [fetcher.fetch_borrow_data(morphoblue_contract, market_id, user_address, provider) for market_id in markets.whitelisted_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for market_id, result in zip(markets.whitelisted_ids, results):
        if isinstance(result, Exception):
            print(f"Error fetching data for market_id: {market_id}: {result}")
        else:
            supply_apy, borrow_apy, borrow_assets_user, market_total_supply,market_total_borrow,health_factor,is_healthy  = result
            print("-------------------------")
            print(f"Results for market_id: {market_id}")
            print(f"supply: {supply_apy * 100} %")
            print(f"borrow_apy: {borrow_apy * 100}%")
            print(f"borrow_assets_user: {borrow_assets_user}")
            print(f"market_total_supply: {market_total_supply}")
            print(f"market_total_borrow: {market_total_borrow}")
            print(f"health_factor: {health_factor}")
            print(f"is_healthy: {is_healthy}")
            print("-------------------------")
if __name__ == "__main__":
    asyncio.run(main())
