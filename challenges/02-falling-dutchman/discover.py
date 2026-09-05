import json
import os

import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

BLOCK = 9462777
DUTCHX = "0xb9812E2fA995EC53B5b6DF34d21f9304762C5497"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
ETH_RPC = os.environ["ETH_RPC_URL"]
w3 = Web3(Web3.HTTPProvider(ETH_RPC))


topic0 = Web3.to_hex(Web3.keccak(text="NewTokenPair(address,address)"))

r = requests.get(
    "https://eth.blockscout.com/api",
    params={
        "module": "logs",
        "action": "getLogs",
        "fromBlock": 7000000,
        "toBlock": BLOCK,
        "address": DUTCHX,
        "topic0": topic0,
    },
).json()

tokens = set()
for log in r["result"]:
    if log["topics"][0] != topic0:
        continue
    tokens.add(Web3.to_checksum_address("0x" + log["topics"][1][-40:]))
    tokens.add(Web3.to_checksum_address("0x" + log["topics"][2][-40:]))

# with open(f"{Path(__file__).parent}/tokens.txt", "w") as f:
#     f.writelines(t + "\n" for t in sorted(tokens))


impl = Web3.to_checksum_address(
    "0x" + w3.eth.get_storage_at(DUTCHX, 0, block_identifier=BLOCK)[-20:].hex()
)
r = requests.get(
    "https://eth.blockscout.com/api",
    params={"module": "contract", "action": "getabi", "address": impl},
).json()
abi = json.loads(r["result"])
dx = w3.eth.contract(address=DUTCHX, abi=abi)

live = []
for t in tokens:
    if t == WETH:
        continue
    if dx.functions.getAuctionStart(WETH, t).call(block_identifier=BLOCK) > 1:
        live.append(t)

for t in live:
    idx = dx.functions.getAuctionIndex(WETH, t).call(block_identifier=BLOCK)
    n1, d1 = dx.functions.getCurrentAuctionPrice(WETH, t, idx).call(
        block_identifier=BLOCK
    )  # n1/d1 -> 1 WETH -> n1/d1 t
    n2, d2 = dx.functions.getCurrentAuctionPrice(t, WETH, idx).call(
        block_identifier=BLOCK
    )  # n2/d2 -> 1 t -> n2/d2 WETH
    if d1 == 0 or d2 == 0:
        continue
    prod = (n1 / d1) * (n2 / d2)
    vol = dx.functions.sellVolumesCurrent(WETH, t).call(block_identifier=BLOCK)
    print(t, "product", prod, "multiple", 1 / prod, "WETH on offer", vol / 1e18)

# address: 0xdd974D5C2e2928deA5F71b9825b8b646686BD200
# product 0.0005331751685496058 multiple 1875.5562130177516 WETH on offer 4.482232591529074
# fair is 1, here it's 0.0005
