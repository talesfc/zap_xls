import os
import sys
import importlib.util
import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.styles import Font, Fill, Alignment
from openpyxl.styles.fonts import _no_value

# importa rotinas de utilidades e de acesso ao banco de dados
# sys.path.append(str(CommonFolderPath))

def writeLog(msg, iflag):
    if(iflag <= 0):
        print(msg)
    if(iflag > 0):
        print(msg)



       


