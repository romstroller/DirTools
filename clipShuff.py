
import random
import pandas as pd

def shuffleClipList():
    
    if itemsDF.shape[0] <= 2: return print(nan)
    # pd clipboard method takes first item as colName; reinsert as row
    el = itemsDF.columns[0]
    itemsDF.columns = [ "items" ]
    itemsDF.loc[-1] = el
    itemsDF.sort_index(inplace=True)
    print( f"{itemsDF.shape[0]} ITEMS FROM CLIPBOARD:\n", itemsDF, "\n")
    itemsDF_shuff = itemsDF.sample(frac=1).reset_index(drop=True)
    
    # rand re-insert 1st row if unmoved, and even callously dismissive
    if itemsDF_shuff.loc[0].values == itemsDF.loc[0].values:
        # get rand loc in df range (not at start or end)
        def randLoc(): return random.randrange(itemsDF_shuff.shape[0]-1)
        rLoc = randLoc()
        while rLoc == 0 or rLoc > itemsDF_shuff.shape[0]-1: rLoc = randLoc()
        
        # split at loc, and join around row
        itemsDF_shuff = pd.concat( [
            itemsDF_shuff.loc[1:rLoc],
            itemsDF_shuff.loc[0:0],
            itemsDF_shuff.loc[rLoc+1:],
            ], ignore_index=True)
    
    return [ v for v in itemsDF_shuff["items"].values ]

errs = ( StopIteration, pd.errors.EmptyDataError, pd.errors.ParserError ) 

while True:
    try: itemsDF = pd.read_clipboard()
    except errs: pass
    nan = "Clipped not single-column list of 4+ items."
    try: sh = itemsDF.shape[0]
    except NameError: print(nan)
    else:
        shuff = shuffleClipList()
        pd.io.clipboard.copy("\n".join(shuff))
        print( "SHUFFLED, COPIED TO CLIPBOARD:\n")
        for el in shuff: print( el )
    input( "\nenter to reshuffle\n" )
    
# EXTEND: allow multi-column clip shuffle

