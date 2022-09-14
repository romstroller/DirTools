import os
import re
import json
import time
import shutil
import pickle
import pandas as pd
from datetime import datetime

# for kaggle authenticate
from kaggle.api.kaggle_api_extended import KaggleApi
from zipfile import ZipFile
from pathlib import Path


class OsKit():
    ''' frequently used app-file interactions '''
    
    def datesortFiles( self, dpath, filt=None ):
        ''' dict of fname  and date modified, 
            descending by date (new first).
            and filt to filter by string'''
        
        if filt: dirList = [ i for i in os.listdir(dpath) if filt in i ]
        else: dirList = os.listdir(dpath)
        
        fNamesDated = {}
        for i in dirList: fNamesDated[i] = os.path.getmtime(i)
        
        fNamesSorted = dict(
            sorted(
                fNamesDated.items(), 
                key=lambda item: item[1], 
                reverse=True ))
        
        fDTimeFMTD = {}
        for i in fNamesSorted: 
            dtString = datetime.fromtimestamp(fNamesSorted[i])
            fmtString = dtString.strftime("%Y_%m_%d_%H_%M_%S_%f")
            fDTimeFMTD[i] = fmtString
        
        # # implement:
        # latestWithP = dirTools.datesortFiles( os.getcwd(), filt="p")
        # for i in latestWithP: print( f"{latestWithP[i]}: {i}" )
        # list(latestWithP)[0]  # most recent with filter
        
        return fDTimeFMTD
    
    
    def tryRename( self, curName, newName ):
        pos = 0
        while True:
            time.sleep(1)
            try: os.rename( curName, newName )
            except (FileNotFoundError, PermissionError ) as e:
                print( f"RN wait access ({type(e).__name__})\n{newName}" )
                if pos ==10 and input("BREAK to skip") =="BREAK": 
                    self.logDict['tmo_rename'].append(curName)
                    return False
                pos +=1
            else: return True
    
    
    def tryMove( self, namePath, destPath ):
        pos = 0
        while True:
            time.sleep(1)
            try: shutil.move( namePath, destPath )
            except (FileNotFoundError, PermissionError ) as e:
                print( f"Move wait access ({type(e).__name__})\n{namePath}" )
                if pos ==10 and input("BREAK to skip") =="BREAK": 
                    self.logDict['tmo_move'].append(namePath)
                    return False
                pos +=1
            else: return True       
    
    
    def waitRename( self, prevDirList, link, move=None ):
        ''' wait for expected new files in dir; rename and (if) move '''
        
        print( f"wait-rename for {link}" )
        while True:
            self.randSleep(2, 3)
            dirList = os.listdir(self.tempDL)
            newFNames = [ i for i in dirList if i not in prevDirList ]
            if newFNames == 0: print("await download"); continue
            
            downloading = False
            for fName in newFNames:
                if ".part" in fName:
                    print( f"wait partfile {fName}" )
                    downloading = True; break
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
    
    
    def cleanString(self, tit, prfx="", suff=None, isFile=False, stamp=False):
        
        if len(prfx)>0: prfx = prfx+'_'
        cleaned = f"{prfx}{self.dtStamp()}_" if stamp else prfx
        if isFile: extPos = tit.rfind('.')
        pos = 0    
        for i in tit:
            if isFile and pos == extPos: cleaned +=tit[pos]
            elif re.match("[A-Za-z0-9]*$", i): cleaned +=i
            else: cleaned +='_'
            pos +=1
        if suff: cleaned += suff
        return cleaned
    
    
    def dtStamp( self ):
        datetimenow = datetime.now()
        return datetimenow.strftime("%y%m%d_%H%M%S%f")    
    
    
    def storePKL( self, item, fName, root, subdir=None  ):
        if subdir: root = root + f'\\{subdir}'
        if not os.path.exists(root): os.makedirs(root)
        with open ( f"{root}\\{fName}.pkl", "wb") as file:
            pickle.dump(item, file)
    
    def getKaggleSet( self, owner, dSetTitle, keyPath = None ):
        """
        Authenticate with Kaggle, download datasete and load to Pandas
        Authentication looks for your Kaggle key file at the defined path
        implement eg: 
            df = getKaggleSet( 'osmi', 'mental-health-in-tech-2016' )
        """
        
        # authenticate with API
        currWorkDir = os.getcwd()
        userDir = Path.home()
        if not keyPath: keyPath = f"{userDir}\\PYC\\_ADMIN\\kaggle.json"
        
        with open( keyPath, 'r' ) as f: keyDict = json.load( f )
        userTitle, keyTitle = keyDict.keys()
        os.environ[ 'KAGGLE_USERNAME' ] = keyDict[ userTitle ]
        os.environ[ 'KAGGLE_KEY' ] = keyDict[ keyTitle ]
        api = KaggleApi()
        api.authenticate()
        
        # retrieve dataset
        api.dataset_download_files( f'{owner}/{dSetTitle}', path="." )
        
        # await download
        
        datasetFName = None
        print( "Waiting for dataset download" )
        while True:
            time.sleep( 1 )
            sortedFs = self.datesortFiles( currWorkDir, dSetTitle )
            if len( sortedFs ) == 0: continue
            datasetFName = list( sortedFs )[ 0 ]
            print( f"Latest: {datasetFName}" )
            break
        
        # extract and identify datafiles
        orDataDir = f"{currWorkDir}\\data_or"
        if not os.path.exists(orDataDir): os.makedirs(orDataDir)
        if datasetFName and Path( datasetFName ).suffix == ".zip":
            with ZipFile( datasetFName, 'r' ) as zipF: 
                zipF.extractall(orDataDir)
        dataPaths = [ f"{orDataDir}\\{pth}" for pth in os.listdir(orDataDir)
            if Path( pth ).suffix == ".csv" ]
        if len( dataPaths ) > 0:
            # dfOrig = 
            print( "Got DF from extracted dSet at:\n", dataPaths[ 0 ] )
            return pd.read_csv( [ pth for pth in dataPaths ][ 0 ] )
        else: print( "Failed get CSV" ); return None
