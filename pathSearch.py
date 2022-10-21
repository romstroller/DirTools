
import os
import re
import subprocess


def getInp(): return input( "\nEnter search terms or '~' to break: " )

def getPattern( _inp):
    inSplit = [ c for c in re.split("[-_\.\s,]+", _inp.lower()) if len(c)>0 ]
    if not inSplit: return _inp  # in case a file is named only with seps ?
    
    patt = inSplit.pop(0)
    # prefix segment with "not slash". use an "any (.)" to match whole path
    while len(inSplit)>1:
        if len(p:= inSplit.pop(0) )>0: patt+= f".*{p}"
    
    if inSplit: patt+= r"[^\\]*" + inSplit.pop(0)
    
    return re.compile(patt)

def getWalkDct(): return { 
    path : { "folds" : sDirs, "files" : files }
    for path, sDirs, files in os.walk(".") }

def getAction( _rslts ):
    
    def getActRef(): return input( f"\n"
        f"[ g 4 ] - go to result 4 in explorer\n"
        f"[ o 7 ] - run/open result 7\n"
        f"[ p 2 ] - print full path for result 2\n"
        f"[  s  ] - run a new search\n"
        f"[  ~  ] - exit pathSearch utility\n\n" )
    
    def getRefPath( _inp ):
        try: num = int(_inp[1:])
        except ValueError: pass
        else:
            for rNum, fil, pth in _rslts:
                if num == rNum: return f"{pth}\\{fil}" if fil else pth
        print( f"Result reference missing or invalid: [ {_inp} ]" )
    
    def goTo( _inp ):
        rPth = getRefPath( _inp )
        if rPth: subprocess.Popen(r'explorer /select,' + rPth)
        
    def start( _inp ): 
        rPth = getRefPath( _inp )
        if rPth: os.startfile(rPth)
        
    def getPath( _inp ):
        rPth = getRefPath( _inp )
        if rPth: print( os.getcwd() + rPth[1:] )
    
    while True:
        inp = getActRef()
        if not inp: continue
        match inp[0]:
            case 'g' | 'G': goTo(inp)
            case 'o' | 'O': start(inp)
            case 'p' | 'P': getPath(inp)
            case 's' | 'S': return getInp()
            case '~': return inp
            case _: print(f'Not action at first position: [ {inp[0]} ]')



# MAIN

os.chdir( os.path.dirname( os.path.abspath( __file__ )))

inp = getInp()

while inp != "~":
    
    patt = getPattern( inp)
    rsltDex = []
    rNum = 1
    
    # match input variations in new os.walk
    for pth, dct in getWalkDct().items():
            
        # store path if match segment not in a prev. matched parent
        if re.findall( patt, pth.lower() ):
            
            stored = False
            for rslt in rsltDex:
                # stored True if not match any pth minus prev. results
                if True not in [ True for el in pth.split(rslt[2]) 
                    if re.findall( patt, el.lower() ) ]:
                    stored = True
                    break
                    
            if not stored:
                rsltDex.append( ( rNum, None, pth ) )
                rNum +=1
        
        # store any matching files at path
        for fil in dct['files']:
            if re.findall( patt, fil.lower() ):
                rsltDex.append( ( rNum, fil, pth ) )
                rNum +=1
    
    # output any results indexed
    for num, fil, pth in rsltDex:
        loc = f"FILE [ {fil} ]" if fil else "PATH"
        print( f"MATCH [ {num} ] IN {loc}:\n   AT [ {pth} ]" )
        
    # offer action
    if len( rsltDex ) == 0: 
        print( "No results" )
        inp = getInp()
    else: inp = getAction( rsltDex )

