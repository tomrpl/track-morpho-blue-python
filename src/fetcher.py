# fetcher.py

import json
from .types import MarketParams, MarketState, PositionUser
from utils.maths import w_div_down, w_div_up, w_taylor_compounded, w_mul_down
from utils.shares import to_assets_up, to_shares_down
from .constants import MAX_UINT256, ORACLE_PRICE_SCALE, SECONDS_PER_YEAR, IRM_ADDRESS, WAD, ZERO_ADDRESS

with open('./abis/AdaptiveCurveIRM.json') as f:
    irm_abi = json.load(f)

with open('./abis/ChainlinkOracle.json') as f:
    oracle_abi = json.load(f)

async def fetch_borrow_data(morphoblue_contract, market_id, user_address, provider):
    try:
        block = provider.eth.get_block('latest')
        market_params = MarketParams(*morphoblue_contract.functions.idToMarketParams(market_id).call())
        market_state = MarketState(*morphoblue_contract.functions.market(market_id).call())
        position_user = PositionUser(*morphoblue_contract.functions.position(market_id, user_address).call())
        print('position_user', position_user)
        market_params_tuple = (
            market_params.loan_token,
            market_params.collateral_token,
            market_params.oracle,
            market_params.irm,
            market_params.lltv,
        )

        market_state_tuple = (
            market_state.total_supply_assets,
            market_state.total_supply_shares,
            market_state.total_borrow_assets,
            market_state.total_borrow_shares,
            market_state.last_update,
            market_state.fee,
        )
        morphoblueirm_contract = provider.eth.contract(address=IRM_ADDRESS, abi=irm_abi)

        borrow_rate = morphoblueirm_contract.functions.borrowRateView(market_params_tuple, market_state_tuple).call()
        borrow_apy = w_taylor_compounded(borrow_rate, SECONDS_PER_YEAR)
        market_state_updated = accrue_interests(int(block['timestamp']), market_state, borrow_rate)
        market_total_borrow = market_state_updated.total_borrow_assets 
        borrow_assets_user = to_assets_up(position_user.borrow_shares, market_state_updated.total_borrow_assets, market_state_updated.total_borrow_shares)
        if (market_params.irm != ZERO_ADDRESS):
            if market_total_borrow == 0:
                utilization = 0
            else:
                utilization = w_div_up(market_total_borrow, market_state_updated.total_supply_assets)
            supplyApy = w_mul_down(w_mul_down(borrow_apy, (WAD - market_state.fee)), utilization)
        
        oracle_contract = provider.eth.contract(address=market_params.oracle, abi=oracle_abi)  
        collateral_price = oracle_contract.functions.price().call()
        collateral = position_user.collateral  
        max_borrow = w_mul_down(
            w_div_down(collateral * collateral_price, ORACLE_PRICE_SCALE),
            market_params.lltv
        )

        # Determine if the position is healthy
        is_healthy = max_borrow >= borrow_assets_user
        health_factor = MAX_UINT256 if borrow_assets_user == 0 else w_div_down(max_borrow, borrow_assets_user)
        return supplyApy/WAD, borrow_apy/WAD, borrow_assets_user, market_state_updated.total_supply_assets, market_total_borrow, health_factor/WAD**2, is_healthy
    
    except Exception as e:
        return e
    

def accrue_interests(last_block_timestamp, market_state: MarketState, borrow_rate):
    elapsed = last_block_timestamp - market_state.last_update
    if elapsed == 0:
        return market_state
    if market_state.total_borrow_assets != 0:
        interest = w_mul_down(
            market_state.total_borrow_assets,
            w_taylor_compounded(borrow_rate, elapsed)
        )
        # Create a new MarketState with updated totals
        market_with_new_total = MarketState(
            market_state.total_supply_assets + interest,
            market_state.total_supply_shares,  # Will be updated below if there's a fee
            market_state.total_borrow_assets + interest,
            market_state.total_borrow_shares,
            market_state.last_update,
            market_state.fee
        )
        if market_state.fee != 0:
            fee_amount = w_mul_down(interest, market_state.fee)
            fee_shares = to_shares_down(
                fee_amount,
                market_with_new_total.total_supply_assets - fee_amount,
                market_with_new_total.total_supply_shares
            )
            # Update the total supply shares with the fee shares
            market_with_new_total.total_supply_shares += fee_shares

        return market_with_new_total
    return market_state
