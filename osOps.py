import os
import re
import json
import time
import shutil
import pickle
import inspect
import pandas as pd
from datetime import datetime

# # for kaggle authenticate
# from kaggle.api.kaggle_api_extended import KaggleApi
# from zipfile import ZipFile
# from pathlib import Path


class Ops():
    ''' frequently used app-file interactions '''
    
    def datesortFiles( self, pth, filt = None, starts = True ):
        ''' list of fname and date modified, ordered by last modified.
            if filt, must contain filt; if startswith, must start with filt. '''
        
        if starts: fNs = [ n for n in os.listdir( pth ) if n.startswith(filt) ]
        elif filt: fNs = [ n for n in os.listdir( pth ) if n == filt ]
        else: fNs = os.listdir( pth )
        
        fNamesDated = [ 
            ( n, datetime.fromtimestamp( os.path.getmtime( n ) ) )
            for n in fNs 
            ]
        
        fNamesSortd = sorted(
            fNamesDated,
            key = lambda item: item[ 1 ],
            reverse=True 
            )
            
        fNDateFrmtd = [
            ( n, tStr.strftime( "%y%m%d_%H%M%S%f" ) )
            for n, tStr in fNamesSortd
            ]
        
        return fNDateFrmtd
    
    def tryRename( self, curName, newName ):
        pos = 0
        while True:
            time.sleep( 1 )
            try: os.rename( curName, newName )
            except (FileNotFoundError, PermissionError) as e:
                print( f"RN wait access ({type( e ).__name__})\n{newName}" )
                if pos == 10 and input( "BREAK to skip" ) == "BREAK":
                    self.logDict[ 'tmo_rename' ].append( curName )
                    return False
                pos += 1
            else: return True
    
    def tryMove( self, namePath, destPath ):
        pos = 0
        while True:
            time.sleep( 1 )
            try: shutil.move( namePath, destPath )
            except (FileNotFoundError, PermissionError) as e:
                print( f"Move wait access ({type( e ).__name__})\n{namePath}" )
                if pos == 10 and input( "BREAK to skip" ) == "BREAK":
                    self.logDict[ 'tmo_move' ].append( namePath )
                    return False
                pos += 1
            else: return True
    
    def waitRename( self, prevDirList, link, move = None ):
        ''' wait for expected new files in dir; rename and (if) move '''
        
        print( f"wait-rename for {link}" )
        while True:
            self.randSleep( 2, 3 )
            dirList = os.listdir( self.tempDL )
            newFNames = [ i for i in dirList if i not in prevDirList ]
            if newFNames == 0: print( "await download" ); continue
            
            downloading = False
            for fName in newFNames:
                if ".part" in fName:
                    print( f"wait partfile {fName}" )
                    downloading = True;
                    break
            if downloading: continue
            
            for fName in [ i for i in newFNames if ".part" not in i ]:
                print( f"stamping file {fName}" )
                crName = f"{self.tempDL}\\{fName}"
                nwName = f"{self.tempDL}\\{self.dtStamp()}_{fName}"
                
                rn = self.tryRename( crName, nwName )
                if not rn: return false
                if rn and move:
                    mv = self.tryMove( nwName, move )
                    return True if mv else False
            return
    
    def cleanString( self, tit, prfx = "", suff = None, isFile = False, 
        stamp = False ):
        if len( prfx ) > 0: prfx = prfx + '_'
        cleaned = f"{prfx}{self.dtStamp()}_" if stamp else prfx
        if isFile: extPos = tit.rfind( '.' )
        pos = 0
        for i in tit:
            if isFile and pos == extPos: cleaned += tit[ pos ]
            elif re.match( "[A-Za-z0-9]*$", i ): cleaned += i
            else: cleaned += '_'
            pos += 1
        if suff: cleaned += suff
        return cleaned
    
    def dtStamp( self ):
        datetimenow = datetime.now()
        return datetimenow.strftime( "%y%m%d_%H%M%S%f" )
    
    def storePKL( self, item, fName, loc, stamp=True, subd=None ):
        if subd: loc = loc + f'\\{subd}'
        if not os.path.exists( loc ): os.makedirs( loc )
        if stamp: fName = f"{fName}_{self.dtStamp()}"
        with open( (pth := f"{loc}\\{fName}.pkl"), "wb" ) as file:
            pickle.dump( item, file )
        return pth
    
    def unPklData( self, loc, fName, latest = True ):
        
        filesByLatest = [ open( fpth, 'rb' ) 
            for fpth, _ in self.datesortFiles( loc, fName ) 
            if fpth.endswith('.pkl')
            ]
        
        try: return ( pickle.load( filesByLatest[0] ) if latest 
            else { fObj.name: pickle.load( fObj ) for fObj in filesByLatest } )
        finally: [ fi.close() for fi in filesByLatest ]
    
    def setCWDtoFile( self ):
        os.chdir( os.path.dirname( os.path.abspath( __file__ ) ) )
    
    def getDirTreeDict( self, _root = None ):
        
        os.chdir( ( os.path.dirname( os.path.abspath( __file__ )) )
            if not _root else _root )

        # get all paths and files-at-path in dict
        rootWalk = { path : { "folds" : sDirs, "files" : files }
            for path, sDirs, files in os.walk(".") }

        dirTree = { }
        for path, items in rootWalk.items():
            
            # get path as sequence of directories
            sDirs = [ sDir.strip(os.sep) for sDir in path.split(os.sep) ]
            node = dirTree  # restart at root
            
            while len(sDirs) > 0:
                
                sDir = sDirs.pop( 0 )  # take leftmost dir in path
                # if not "sDirs", create and add empty subDict
                if not node.get( "folds" ): node.update( 
                    { "folds" : { sDir : {} } } )
                else:  # if not sDict, create
                    if not node["folds"].get(sDir):
                        node["folds"].update( { sDir : {} } )
                node = node[ "folds" ][ sDir ]  # move to branch
                
            node.update( { "files": items["files"] } )  # add files end sDirseq
            
        return dirTree, rootWalk
    
    # def getKaggleSet( self, owner, dSetTitle, keyPath = None ):
        # """
        # Authenticate with Kaggle, download datasete and load to Pandas
        # Authentication looks for your Kaggle key file at the defined path
        # """
        
        # def download():
            # if not keyPath: keyPath = f"{userDir}\\PYC\\_ADMIN\\kaggle.json"
            # with open( keyPath, 'r' ) as f: keyDict = json.load( f )
            # userTitle, keyTitle = keyDict.keys()
            # os.environ[ 'KAGGLE_USERNAME' ] = keyDict[ userTitle ]
            # os.environ[ 'KAGGLE_KEY' ] = keyDict[ keyTitle ]
            # api = KaggleApi()
            # api.authenticate()
            # api.dataset_download_files( f'{owner}/{dSetTitle}', path="." )
            # return True
        
        # downloadStarted = False
        # currWorkDir = os.getcwd()
        # userDir = Path.home()
        # dataFname = None
        
        # while not dataFname:
            # sortedFs = self.datesortFiles( currWorkDir, dSetTitle )
            # if len( sortedFs ) == 0:
                # if not downloadStarted: downloadStarted = download()
                # else: print( f"- [{self.dtStamp()}] Await Kaggle API request" )
                # time.sleep( 1 )
            # else:
                # dataFname, dated = list( sortedFs.items() )[ 0 ]
                # print( f"- [{(st := self.dtStamp())}] Got '{dataFname}'\n"
                       # f"{' ' * (len( st ) + 5)}Dated: {dated}" )
        
        # # extract and identify datafiles
        # datDir = f"{currWorkDir}\\data_or"
        # if not os.path.exists( datDir ): os.makedirs( datDir )
        # if dataFname and Path( dataFname ).suffix == ".zip":
            # with ZipFile( dataFname, 'r' ) as zipf: zipf.extractall( datDir )
        # dataPaths = [ f"{datDir}\\{pth}" for pth in os.listdir( datDir )
            # if Path( pth ).suffix == ".csv" ]
        
        # return (pd.read_csv( [ pth for pth in dataPaths ][ 0 ] )
                # if len( dataPaths ) > 0 else None)
