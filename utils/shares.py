# shares.py

from .maths import mul_div_down, mul_div_up


VIRTUAL_SHARES = 10 ** 6
VIRTUAL_ASSETS = 1

def to_shares_down(assets, total_assets, total_shares):
    return mul_div_down(assets, total_shares + VIRTUAL_SHARES, total_assets + VIRTUAL_ASSETS)

def to_assets_down(shares, total_assets, total_shares):
    return mul_div_down(shares, total_assets + VIRTUAL_ASSETS, total_shares + VIRTUAL_SHARES)

def to_shares_up(assets, total_assets, total_shares):
    return mul_div_up(assets, total_shares + VIRTUAL_SHARES, total_assets + VIRTUAL_ASSETS)

def to_assets_up(shares, total_assets, total_shares):
    return mul_div_up(shares, total_assets + VIRTUAL_ASSETS, total_shares + VIRTUAL_SHARES)
