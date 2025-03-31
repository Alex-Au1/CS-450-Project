import os
import glob
from enum import Enum
from typing import Dict, Optional, List


TxtFileEncoding = "utf-8"
TestPerAlgo = 8


# SimulationKeywords: Some keywords in a simulation result file
class SimulationKeywords(Enum):
    CacheSize = "cache size"


# FileExt: File extensions
class FileExt(Enum):
    Txt = ".txt"
    OracleGeneral = ".oracleGeneral.bin"
    IQIBinTxt = ".IQI.bin.txt"


# ============== PARAMETERS =====================

# The "all" folder that contains all the finalized simulation results
#
# TODO: PLEASE CHANGE THIS UP FOR YOUR OWN COMPUTER
AllFinalizedResultFolder = r"E:\Computer\Programs\C Language\CS450\CS-450-Project\result\project cachesim\all"

# Map of raw simulation results to finalized results
#
# Note: Both files to raw simulation results and finalized results do not necessarily need to exist
SimulationFileMap = {}


# TODO: PLEASE CHANGE THIS UP FOR YOUR OWN COMPUTER
def createSimulationFileMap():
    rawSimulationResultFolder = r"E:\Computer\Programs\C Language\CS450\CS-450-Project\result"
    finalizedSimulationResultFolder = r"E:\Computer\Programs\C Language\CS450\CS-450-Project\result\project cachesim"

    # FIU
    for rawSimFile in glob.glob(os.path.join(rawSimulationResultFolder, "fiu*.bin")):
        baseName = os.path.basename(rawSimFile)
        finalizedSimFile = os.path.join(finalizedSimulationResultFolder, "FIU", baseName.replace(FileExt.OracleGeneral.value, FileExt.Txt.value))
        SimulationFileMap[rawSimFile] = finalizedSimFile

    # MSR    
    for rawSimFile in glob.glob(os.path.join(rawSimulationResultFolder, "msr*.bin")):
        baseName = os.path.basename(rawSimFile)
        finalizedBaseName = baseName.replace(FileExt.OracleGeneral.value, FileExt.IQIBinTxt.value).replace("msr_", "")
        finalizedSimFile = os.path.join(finalizedSimulationResultFolder, "MSR", finalizedBaseName)
        SimulationFileMap[rawSimFile] = finalizedSimFile

    # CloudPhysics
    for rawSimFile in glob.glob(os.path.join(rawSimulationResultFolder, "w*.bin")):
        baseName = os.path.basename(rawSimFile)
        finalizedSimFile = os.path.join(finalizedSimulationResultFolder, "Cloudphysics", baseName.replace(FileExt.OracleGeneral.value, FileExt.Txt.value))
        SimulationFileMap[rawSimFile] = finalizedSimFile

    # Alibaba
    for rawSimFile in glob.glob(os.path.join(rawSimulationResultFolder, "io_traces.ns*.bin")):
        baseName = os.path.basename(rawSimFile)
        finalizedSimFile = os.path.join(finalizedSimulationResultFolder, "AlibabaBlock", baseName.replace(FileExt.OracleGeneral.value, FileExt.Txt.value))
        SimulationFileMap[rawSimFile] = finalizedSimFile

    # Tencent
    for rawSimFile in glob.glob(os.path.join(rawSimulationResultFolder, "tencentBlock.ns*.bin")):
        baseName = os.path.basename(rawSimFile)
        finalizedSimFile = os.path.join(finalizedSimulationResultFolder, "TencentBlock", baseName.replace(FileExt.OracleGeneral.value, FileExt.Txt.value))
        SimulationFileMap[rawSimFile] = finalizedSimFile

createSimulationFileMap()

# ===============================================


# SimCollector: Class for updating raw output results from the simulation into 
#   the finalized output result of the project
class SimCollector():
    def __init__(self, allFinalizedResultFolder: str):
        self.allFinalizedResultFolder = allFinalizedResultFolder

    def __call__(self, simFileMap: Dict[str, str]):
        return self.collect(simFileMap)
    
    # getAlgoId(line): Retrieves the id of a line
    @classmethod
    def getAlgoId(cls, line: str) -> Optional[str]:
        cacheSizeInd = line.find(SimulationKeywords.CacheSize.value)
        if (cacheSizeInd == -1):
            return None
        
        idEnd = cacheSizeInd + len(SimulationKeywords.CacheSize.value)
        return line[:idEnd]
    
    # readFileLines(file, raiseError): 
    @classmethod
    def readFileLines(cls, file: str, raiseError: bool = False) -> List[str]:
        result = []

        try:
            with open(file, "r", encoding = TxtFileEncoding) as f:
                result = f.readlines()
        except FileNotFoundError as e:
            if (raiseError):
                raise e
            return result
        
        return result

    # collectSimulation(simulationFile): Collects the raw result from cachesim and updates
    #   the latest result into the finalized simulation file
    def collectSimulation(self, simulationFile: str, collectedFile: str):
        simFileLines = []

        try:
            simFileLines = self.readFileLines(simulationFile, raiseError = True)
        except FileNotFoundError:
            return
        
        algosFileInd = {}
        simFileLinesLen = len(simFileLines)

        # get the latest result for each algo in the simulation
        for fileInd in range(0, simFileLinesLen, TestPerAlgo):
            simLine = simFileLines[fileInd]
            algoId = self.getAlgoId(simLine)
            algosFileInd[algoId] = fileInd

        collectedFileLines = self.readFileLines(collectedFile, raiseError = False)
        collectedFileLinesLen = len(collectedFileLines)

        # remove the old algo results
        for fileInd in range(collectedFileLinesLen):
            collectedLine = collectedFileLines[fileInd].strip()
            algoId = self.getAlgoId(collectedLine)
            if (algoId in algosFileInd or collectedLine == ""):
                collectedFileLines[fileInd] = None

        collectedFileLines = list(filter(lambda fileLine: fileLine is not None, collectedFileLines))

        # add the updated algo results
        for algoId in algosFileInd:
            algoFileInd = algosFileInd[algoId]
            collectedFileLines += simFileLines[algoFileInd : algoFileInd + TestPerAlgo]

        newCollectedStr = "".join(collectedFileLines)

        # write back the new result
        with open(collectedFile, "w+", encoding = TxtFileEncoding) as f:
            f.write(newCollectedStr)

        # copy the new result to the "all" folder
        collectedFileAllCopy = os.path.join(self.allFinalizedResultFolder, os.path.basename(collectedFile))
        with open(collectedFileAllCopy, "w+", encoding = TxtFileEncoding) as f:
            f.write(newCollectedStr)

    # collect(simFileMap): 
    def collect(self, simFileMap: Dict[str, str]):
        for simulationFile in simFileMap:
            collectedFile = simFileMap[simulationFile]
            self.collectSimulation(simulationFile, collectedFile)


############
#   MAIN   #
############
if __name__ == '__main__':
    collector = SimCollector(AllFinalizedResultFolder)
    collector(SimulationFileMap)