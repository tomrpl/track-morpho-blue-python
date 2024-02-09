# fetcher.py
from decimal import Decimal, getcontext
import json
from .types import MarketParams, MarketState, PositionUser
from utils.maths import w_div_up, w_taylor_compounded, w_mul_down
from utils.shares import to_assets_up, to_shares_down
from .constants import SECONDS_PER_YEAR, IRM_ADDRESS, WAD, ZERO_ADDRESS

getcontext().prec = 18

with open('./abis/AdaptiveCurveIRM.json') as f:
    irm_abi = json.load(f)

async def fetch_borrow_data(morphoblue_contract, market_id, user_address, provider):
    try:
        block = provider.eth.get_block('latest')
        market_params = MarketParams(*morphoblue_contract.functions.idToMarketParams(market_id).call())
        market_state = MarketState(*morphoblue_contract.functions.market(market_id).call())
        position_user = PositionUser(*morphoblue_contract.functions.position(market_id, user_address).call())

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
        market_state_updated = accrue_interests(Decimal(block['timestamp']), market_state, borrow_rate)
        market_total_borrow = market_state_updated.total_borrow_assets 
        borrow_assets_user = to_assets_up(position_user.borrow_shares, market_total_borrow, market_state_updated.total_borrow_shares)

        if (market_params.irm != ZERO_ADDRESS):
            if market_total_borrow == 0:
                utilization = 0
            else:
                utilization = w_div_up(market_total_borrow, market_state_updated.total_supply_assets)
            supplyApy = w_mul_down(w_mul_down(borrow_apy, (WAD - market_state.fee)), utilization)
        

        return supplyApy/WAD, borrow_apy/WAD, borrow_assets_user, market_state_updated.total_supply_assets, market_total_borrow
    
    except Exception as e:
        return e
    

def accrue_interests(last_block_timestamp, market_state: MarketState, borrow_rate):
    elapsed = last_block_timestamp - market_state.last_update
    if elapsed == 0:
        return market_state
    if market_state.total_borrow_assets != 0:
        interest = w_mul_down(
            Decimal(market_state.total_borrow_assets),
            w_taylor_compounded(Decimal(borrow_rate), Decimal(elapsed))
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
            fee_amount = w_mul_down(interest, Decimal(market_state.fee))
            fee_shares = to_shares_down(
                fee_amount,
                market_with_new_total.total_supply_assets - fee_amount,
                market_with_new_total.total_supply_shares
            )
            # Update the total supply shares with the fee shares
            market_with_new_total.total_supply_shares += fee_shares

        return market_with_new_total
    return market_state
