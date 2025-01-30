#
""" 
- for each .txt file in INFolderPath 
  - take chat name from input file name
  - creates in XLSFolderPath folder a .xlsx file with same name as input file 
  - moves input text files to OUTFolderPath 
"""
#
import os
import sys
import importlib.util
import datetime
import shutil

from pathlib import Path

# gets script name and paths
Script= sys.argv[0]
ScriptFolderPath= Path(Script).parent 
ParentFolderPath= Path(ScriptFolderPath).parent 

UtilsFolderPath= Path.joinpath(ScriptFolderPath,'utils')

INFolderPath= Path.joinpath(ScriptFolderPath,'files_txt_in')
OUTFolderPath= Path.joinpath(ScriptFolderPath,'files_txt_out')
XLSFolderPath= Path.joinpath(ScriptFolderPath,'files_xlsx_out')

sys.path.append(str(ScriptFolderPath))
sys.path.append(str(UtilsFolderPath))
print("\nsys.path=",str(sys.path))

import Chat_Utils as UTILS_CHAT
import Chat_Xlsx  as CHAT_XLSX

#
listFiles= os.listdir(INFolderPath) 
nfiles= len(listFiles) - 1
#
idchat=0
list_post=[]
list_event=[]
idevent=0
idpost=0
idnote=0
i=0
while(nfiles > 0 and i < nfiles):
    chat_file_name= listFiles[i]
    chat_file_path= Path.joinpath(INFolderPath, chat_file_name)
    print(f"\nScript={Script}, Chat_file:{chat_file_path}")
    #
    # Abre o arquivo com dados do Chat e processa registros
    i += 1
    fp = open(chat_file_path, 'r', encoding="utf8")
    freader= fp.readlines()
    row0= freader[0]
    length= len(row0)
    if length < 1:
        print(f"\nEmpty file!")
        continue
    #
    # create workbook based on xlsx template
    templatefile= 'template.xlsx'
    wbook= CHAT_XLSX.build_WBook(templatefile)
    eventSheet= wbook["Events"]
    postSheet= wbook["Posts"]
    noteSheet= wbook["Notes"]
    idnote= 1
    noteSheet= CHAT_XLSX.insert_notesheet(noteSheet, idnote, "workbook created from template", f"{templatefile}")
    idnote += 1
    noteSheet= CHAT_XLSX.insert_notesheet(noteSheet, idnote, "chat file opened", f"{chat_file_path}")
    #
    # Identifica Plano com base no nome do arquivo
    Grupo= UTILS_CHAT.getGrupo_from_file(listFiles[i])
    idnote += 1
    noteSheet= CHAT_XLSX.insert_notesheet(noteSheet, idnote, "chat file group identified", f"{Grupo}")
    #
    # Identifica padrão de datahora do chat
    date_pattern= UTILS_CHAT.get_Pattern_DataHora(row0)
    idnote += 1
    noteSheet= CHAT_XLSX.insert_notesheet(noteSheet, idnote, "chat file date pattern", f"{date_pattern}")
    #

    outChat_file= chat_file_name.replace(".txt",".xlsx")
    xls_chat_file_path= Path.joinpath(XLSFolderPath, outChat_file)
    CHAT_XLSX.saveXLSWBook(wbook, xls_chat_file_path)
    #
    nevent= 0
    npost= 0
    id=0
    for row in freader:
        id += 1 
        datahora= UTILS_CHAT.getDataHora(row, date_pattern)
        if datahora is None:
            # no date in the text line: it's not an EVENT nor a new POST, its part of current post message
            npost += 1
            postSheet= CHAT_XLSX.insert_postsheet(postSheet, npost, row, "")
        else:
            # if date mark (" - ") is present, can be either EVENT or POST
            posMarcaData= row.find(UTILS_CHAT.marcaData)
            # if header mark (" : ") is present, it marks end of phone or name part and start of post message
            posMarcaHeader= row.find(UTILS_CHAT.marcaHeader)
            if posMarcaData > 0 and posMarcaHeader > 0: 
                npost += 1
                postSheet= CHAT_XLSX.insert_postsheet(postSheet, npost, row, datahora)
                continue
            # if date mark (" - ") is present without header mark, it is an EVENT line
            else:
                nevent += 1
            # EVENT types
            # Type 1 to 3: PHONE or NAME followed by text and/or emoticons separated by ":" 
            if posMarcaHeader > 0:
                agente= row[posMarcaData+1:posMarcaHeader]
                evento= row[posMarcaHeader+1:]
                eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, agente, evento, datahora)
                continue
            # Type 5: line with event mark (200E, 201E, 202E, 203E, 204E, 205E) 
            posMarca200E_1= row.find(UTILS_CHAT.marca200E_1)
            if posMarca200E_1 > 0:
                row2= row[posMarca200E_1+1:]
                eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, "", row2, datahora)
                continue
            posMarca200E_2= row.find(UTILS_CHAT.marca200E_2)
            if posMarca200E_2 > 0:
                row2= row.replace(UTILS_CHAT.marca200E_2, "")
                eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, "", row2, datahora)
                continue
            # Type 6: line with no event mark => identified by text: entrou, saiu, ...
            for tipo in UTILS_CHAT.event_list:
                pos= row.find(tipo)
                if pos > 0:
                    agente= row[:pos]
                    evento= row[pos:]
                    eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, agente, evento, datahora)
                continue
            # Type 0: 'Canal' Event, no agent identified
            if posMarcaData > 0:
                evento= row[posMarcaData+3:]
                eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, "CANAL", evento, datahora)
                continue
            # Type VCF: VCF card posted 
            posmarcaVCF= row.find(UTILS_CHAT.marcaVCF)
            if posmarcaVCF >= 0:
                nevent += 1        
                eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, "VCF", row, datahora)
                continue
            # 
        continue
    # 
    idnote += 1
    noteSheet= CHAT_XLSX.insert_notesheet(noteSheet, idnote, "import end", f"posts= {npost}, events= {nevent}")
    CHAT_XLSX.saveXLSWBook(wbook, xls_chat_file_path)
    fp.close()
    #
    out_file_path= Path.joinpath(OUTFolderPath, chat_file_name)
    shutil.move(chat_file_path, out_file_path)



