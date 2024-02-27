## Install:

Python version used: 3.9:
if you use conda, t is recommended to create a new environment with the following command:

```bash
conda create -n myenv python=3.9
```

and then activate the environment with:

```bash
conda activate myenv
```

Then install the followings:

```bash
pip install python-decouple web3
```

## Credentials:

add an `RPC_URL` into your .env file

## To run: execute

```bash
python main.py
```

-> Don't forgot to jump into the src/markets.py file and add markets you want to track.
If you don't know where to find the marketID -> Jump into the Morpho [docs/](https://docs.morpho.org/addresses#morpho-blue-whitelisted-markets)

## Versions

Python 3.9.18
Web3 version: 6.15.1
