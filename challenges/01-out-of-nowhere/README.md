# Out of Nowhere - Tier 1

You're on your way to leave the office, when you notice [a $1.5M transfer](https://etherscan.io/tx/0xe7b8d46c3f3e5f727cb42c9dfe7fc36855ab5092cf160e4c8812a2a27a84350b) to 
one of the liquidity providers. But what was the source?

Write your answer into `answer.txt`:

```
origin_tx = 0x...
```

Then:

```
python alpha.py check 01
```

Case and a missing `0x` prefix do not matter.

## Solution

Notice it's a bridge, then decode input data to find STKZ (Stacks Chain) as the chain the usdc was bridged from. Notice that the current allbridge stacks bridge contract is too new. Find the legacy stacks bridge contract. Find the tx corresponding https://explorer.hiro.so/txid/0x36f2d5c245d08de980d0d23e4bd23b088312ce9e4b9845b4fd71930f52aab8fc?chain=mainnet&tab=postConditions.
