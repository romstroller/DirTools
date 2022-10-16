
import os


def getVarPatts( _inp ):
    
    vars_one = [  # capitalization variations
        _inp,
        _inp.upper(),
        _inp.lower(),
        _inp.title(), ]
    
    vars_two = [ ]  # separator variations
    for v in vars_one:
        vars_two.append( v )
        vars_two.append( ".".join(v.split(" ")) )
        vars_two.append( " ".join(v.split(".")) )
    
    return list(set( v for v in vars_two ) )  # remove dups


def getInp(): 
    inp = input( "\nEnter search terms or '~' to break: " )
    print( f"\nSearching for [ {inp} ] ...\n" )
    return inp


os.chdir( os.path.dirname( os.path.abspath( __file__ )))

# all paths and files-at-path as dict
rWalk = { path : { "folds" : sDirs, "files" : files }
    for path, sDirs, files in os.walk(".") }

results = {}
inp = getInp()

while inp != "~":
    
    results.update( { inp: {} } )  # store results for input
    inpVars = getVarPatts( inp )  # get variations from input
    results[inp].update( { var : {} for var in inpVars } )  # dcts for vars
    
    # scan walk
    for pth, dct in rWalk.items():
        for var in inpVars:
            
            # store matching path if segment not already in a stored path
            if var in pth:
                stored = False
                for sPth in results[inp][var].keys():
                    if True not in [ var in el for el in pth.split(sPth) ]:
                        stored = True
                        break
                if not stored: results[inp][var].update( { pth : [] } )
            
            # store matching files at path
            for fil in dct['files']:
                if var in fil:
                    if not results[inp][var].get(pth):
                        results[inp][var].update( { pth : [ fil ] } )
                    else: results[inp][var][pth].append( fil )
    
    # output results
    for var, vDct in results[inp].items():
        for pth, rLis in vDct.items():
            if len( rLis ) == 0: print( f"[ {var} ] IN PATH [ {pth} ]" )
            for f in rLis: print( f"[ {var} ] IN FILE [ {f} ] AT [ {pth} ]" )
    
    inp = getInp()


# EXTD: 
#   - whether pth recorded for match file is itself a match to be displayed
#   - Sort results by [ PATH is match, PTH+FILS, Files NOT pth ]
