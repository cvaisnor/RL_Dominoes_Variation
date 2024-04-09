Create tiles
Create players
Select Current player at random (Shuffler)
Set round = 9
Deal tiles
While not done
    Current player plays
        if len hand == 0
            round done
            break
        if len board == 0
            if round|round or S|S in hand
                play round|round or S|S
            else draw
        elif len board == 1 or 2
            if r|? or s|? in hand
                play r|? or s|?
            else draw
        else
            find playable tiles
            if playable tiles: 
                play playable tile from list
            else:
                if boneyard not empty
                    draw
                else
                    done
        Next player plays
Update scores
current player = winner of round
round -= 1
If round >= 0
    play next round


find playable tiles
    Tiles where one end is S or is in exposed ends




receive tile on board
    first tile
        must be double R or double S
        add to list of tiles
        add R to exposed ends
        exposed double = True
    second tile
        must have R or S as end
        add to list of tiles


        