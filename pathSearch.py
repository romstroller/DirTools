
import os
import subprocess


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


def getInp(): return input( "\nEnter search terms or '~' to break: " )


def getAction( _rslts ):
    
    def getActRef(): return input( f"\n"
        f"[ g 4 ] - go to result 4 in explorer\n"
        f"[ o 7 ] - run/open result 7\n"
        f"[  s  ] - run a new search\n"
        f"[  ~  ] - exit pathSearch utility\n\n" )
    
    def getRefPath( _inp ):
        try: num = int(_inp[1:])
        except ValueError: pass
        else:
            for rNum, var, fil, pth in _rslts:
                if num == rNum: return f"{pth}\\{fil}" if fil else pth
        print( f"Result reference missing or invalid: [ {_inp} ] " )
    
    def goTo( _inp ):
        rPth = getRefPath( _inp )
        if rPth: subprocess.Popen(r'explorer /select,' + rPth)
        
    def start( _inp ): 
        rPth = getRefPath( _inp )
        if rPth: os.startfile(rPth)
    
    
    while True:
        inp = getActRef()
        if not inp: continue
        match inp[0]:
            case 'g' | 'G': goTo(inp)
            case 'o' | 'O': start(inp)
            case 's' | 'S': return getInp()
            case '~': return inp
            case _: print(f'Not action at first position: [ {inp[0]} ]')



# MAIN

os.chdir( os.path.dirname( os.path.abspath( __file__ )))


# all paths and files-at-path as dict
rWalk = { path : { "folds" : sDirs, "files" : files }
    for path, sDirs, files in os.walk(".") }


inp = getInp()

while inp != "~":
    
    inpVars = getVarPatts( inp )  # get variations from input
    
    rsltDex = []
    rNum = 1
    
    # match input variations in new os.walk
    for pth, dct in rWalk.items():
        for var in inpVars:
            
            # store path if matching segment not in a prev. matched parent
            if var in pth:
                
                stored = False
                for rslt in rsltDex:
                    if True not in [ var in el for el in pth.split(rslt[3]) ]:
                        stored = True
                        break
                        
                if not stored:
                    rsltDex.append( ( rNum, var, None, pth ) )
                    rNum +=1
            
            # store any matching files at path
            for fil in dct['files']:
                if var in fil:
                    rsltDex.append( ( rNum, var, fil, pth ) )
                    rNum +=1
    
    # output any results indexed
    for num, var, fil, pth in rsltDex:
        loc = f"FILE [ {fil} ]" if fil else "PATH"
        print( f"MATCH [ {num} ] IN {loc}:\n   AT [ {pth} ]" )
        
    # offer action
    if len( rsltDex ) == 0: 
        print( "No results" )
        inp = getInp()
    else: inp = getAction( rsltDex )


# inp "z for" doesn't match pth " Z for " - neither title nor lower.
#     !!! since win OS treats caps same, 
#     can simplify Vars by make each path Lcase after walk

# EXTD:
#   - need to match irregular uppercase on searches of >1 terms
#     as not currently matching eg. "the big Hat"
#   - whether pth recorded for match file is itself a match to be displayed
#   - Sort results by [ PATH is match, PTH+FILS, Files NOT pth ]