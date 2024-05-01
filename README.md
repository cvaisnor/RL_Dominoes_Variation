# Simplified Dominoes Variation for RL

# Rules
## Tiles
- Range [0-9, 0-9]
- Example for [0-3]
    - 00, 01, 02, 03, 11, 12, 13, 22, 23, 33 (Count 10)

## Players
- 2 - N

## Hands
- 2-9 tiles per player

## Rules
1. Player who has highest double tile plays first
    - If no double, draw until available
2. Next player must play tile to matching end
    - If no tile, draw 1 tile (and can play if valid) then pass
3. Play continues by each player connecting a tile to the ends of the board (only left or right)
4. Episode ends when one player has empty hand. Score is total value of tiles left in hand 
5. Winner has lowest score

## Board Example:
```
Board: 3|3
Player 1: plays 3|2

Board: 3|3 3|2
Player 2: plays 2|1

Board: 3|3 3|2 2|1
Player 1: plays 1|3

Board: 3|3 3|2 2|1 1|3
etc...

```
