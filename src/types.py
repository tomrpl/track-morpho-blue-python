# types.py
class MarketState:
    def __init__(self, total_supply_assets, total_supply_shares, total_borrow_assets, total_borrow_shares, last_update, fee):
        self.total_supply_assets = total_supply_assets
        self.total_supply_shares = total_supply_shares
        self.total_borrow_assets = total_borrow_assets
        self.total_borrow_shares = total_borrow_shares
        self.last_update = last_update
        self.fee = fee

class MarketParams:
    def __init__(self, loan_token, collateral_token, oracle, irm, lltv):
        self.loan_token = loan_token
        self.collateral_token = collateral_token
        self.oracle = oracle
        self.irm = irm
        self.lltv = lltv


class PositionUser:
    def __init__(self, supply_shares, borrow_shares, collateral):
        self.supply_shares = supply_shares
        self.borrow_shares = borrow_shares
        self.collateral = collateral


class Contracts:
    def __init__(self, morpho_blue):
        self.morpho_blue = morpho_blue
