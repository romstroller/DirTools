import random
import pandas as pd


def shuffleClipList():
    # pd clipboard method takes first item as colName; reinsert as row
    _el = itemsDF.columns[ 0 ]
    itemsDF.columns = [ "items" ]
    itemsDF.loc[ -1 ] = _el
    itemsDF.sort_index( inplace=True )
    
    print( f"{itemsDF.shape[ 0 ]} ITEMS FROM CLIPBOARD:\n", itemsDF, "\n" )
    itemsDF_sh = itemsDF.sample( frac=1 ).reset_index( drop=True )
    
    # rand re-insert 1st row if unmoved, and even callously dismissive
    if itemsDF_sh.loc[ 0 ].values == itemsDF.loc[ -1 ].values:
        # get rand loc in df range (not at start or end)
        def randLoc(): return random.randrange( 1, itemsDF_sh.shape[ 0 ] - 1 )
        
        rLoc = randLoc()
        while rLoc == 0 or rLoc > itemsDF_sh.shape[ 0 ] - 1: rLoc = randLoc()
        
        # split at loc, and join around row
        itemsDF_sh = pd.concat( [
            itemsDF_sh.loc[ 1:rLoc ],
            itemsDF_sh.loc[ 0:0 ],
            itemsDF_sh.loc[ rLoc + 1: ],
            ], ignore_index=True )
    
    return [ v for v in itemsDF_sh[ "items" ].values ]


ers = (
    AssertionError,
    StopIteration,
    pd.errors.EmptyDataError,
    pd.errors.ParserError)
    
msg = "Clipped not single-column list of 4+ items."

while True:
    try:
        itemsDF = pd.read_clipboard()
        assert itemsDF.shape[ 0 ] > 2  # len 4+
    except ers: print( msg )
    else:
        shuff = shuffleClipList()
        pd.io.clipboard.copy( "\n".join( shuff ) )
        print( "SHUFFLED, COPIED TO CLIPBOARD:\n" )
        for el in shuff: print( el )
        
    input( "\nenter to shuffle again\n" )

# EXTEND:
#   allow multi-column clip shuffle
