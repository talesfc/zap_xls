#
""" 
- para cada arquivo na pasta Entrada
- extrai os parametros do chat do nome do arquivo 
- registra o arquivo no chatCatalog 
- insere registros do chat em chatData
- atualiza registro do chat no chatCatalog com identificação da instancia zeebe
"""
#
import os
import sys
import importlib.util
import datetime
import shutil

from pathlib import Path


# identifica os parametros de execução definidos na chamada do script
# Define projeto se não for passado na chamada do script ### 
Script= sys.argv[0]
narg= len(sys.argv)
if narg < 2:
    sys.argv = [Script, "MVP-1", '0']

# monta paths conforme local deste script
ScriptFolderPath= Path(Script).parent 
ParentFolderPath= Path(ScriptFolderPath).parent 

UtilsFolderPath= Path.joinpath(ScriptFolderPath,'utils')

INFolderPath= Path.joinpath(ScriptFolderPath,'files_txt_in')
OUTFolderPath= Path.joinpath(ScriptFolderPath,'files_txt_out')
XLSFolderPath= Path.joinpath(ScriptFolderPath,'files_xlsx_out')

sys.path.append(str(ScriptFolderPath))
sys.path.append(str(UtilsFolderPath))
print("\nsys.path=",str(sys.path))

import Base_Utils as UTILS_BASE
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
        print(f"\nArquivo vazio")
        continue
    #
    # create workbook based on xlsx template
    templatefile= 'template.xlsx'
    wbook= CHAT_XLSX.build_WBook(templatefile)
    # open events datasheet
    eventSheet= wbook["Events"]
    print(f"\n eventSheet= {eventSheet.title}")
    # open posts datasheet
    postSheet= wbook["Posts"]
    print(f"\n postSheet= {postSheet.title}")
    # open notes datasheet
    noteSheet= wbook["Notes"]
    print(f"\n noteSheet= {noteSheet.title}")
    idnote= 1
    noteSheet= CHAT_XLSX.insert_notesheet(noteSheet, idnote, "workbook created from template", f"{templatefile}")
    idnote += 1
    noteSheet= CHAT_XLSX.insert_notesheet(noteSheet, idnote, "chat file opened", f"{chat_file_path}")
    #
    # Identifica Plano com base no nome do arquivo
    Grupo= UTILS_CHAT.getGrupo_from_file(listFiles[i])
    print(f"\nTratando registros do grupo: {Grupo}")
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
            # Se nao tem data, não e´ EVENTO: é linha de continuação do POST
            npost += 1
            postSheet= CHAT_XLSX.insert_postsheet(postSheet, npost, row, "")
        else:
            # Se tem Marca de Data (" - "), pode ser EVENTO ou POST
            posMarcaData= row.find(UTILS_CHAT.marcaData)
            # Se tem Marca de Header (" : "), que separa FONE/NOME do texto, então é POST
            posMarcaHeader= row.find(UTILS_CHAT.marcaHeader)
            if posMarcaData > 0 and posMarcaHeader > 0: 
                npost += 1
                postSheet= CHAT_XLSX.insert_postsheet(postSheet, npost, row, datahora)
                continue
            # Se tem tem Marca de Data, sem Marca de Header, é  EVENTO
            else:
                nevent += 1
            # Se Evento, pode ser de vários tipos
            # Tipo 1 a 3: FONE ou NOME seguido de texto e/ou emoticons, separados por ":" 
            if posMarcaHeader > 0:
                agente= row[posMarcaData+1:posMarcaHeader]
                evento= row[posMarcaHeader+1:]
                eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, agente, evento, datahora)
                continue
            # Tipo 5: registro com marca de evento: 200E, 201E, 202E, 203E, 204E, 205E 
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
            # Tipo 6: registro sem marca de evento => identificado pelo texto: entrou, saiu, ...
            for tipo in UTILS_CHAT.event_list:
                pos= row.find(tipo)
                if pos > 0:
                    agente= row[:pos]
                    evento= row[pos:]
                    eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, agente, evento, datahora)
                continue
            # Tipo 0: Evento de Canal, não identifica agente
            if posMarcaData > 0:
                evento= row[posMarcaData+3:]
                eventSheet= CHAT_XLSX.insert_eventsheet(eventSheet, nevent, "CANAL", evento, datahora)
                continue
            # Tipo VCF: Registro de postagem de cartão VCF
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



