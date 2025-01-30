#
""" 
- Rotinas de uso comum
--- getProgramaGrupo(afilename): identifica programa e grupo com base no nome do arquivo
--- getChatAtrib(afilename): coleta atributos adicionais do chat no nome do arquivo
"""
#

import re

# Constantes - padrões de datahora
patterDHY2= "^\d{2}\/\d{2}\/\d{2} \d{2}:\d{2}(:\d{2})? "      # dd/MM/yy hh:mm 
patterDHY4= "^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}(:\d{2})? "      # dd/MM/yyyy hh:mm 
patterDHY2C="^\d{1,2}\/\d{1,2}\/\d{2}, \d{2}:\d{2}(:\d{2})? " # MM/dd/yy, hh:mm - 
patterDH01= "^\[\d{2}\/\d{2}\/\d{2,4} \d{2}\:\d{2}\:\d{2}\]"  #[29/12/2018 21:09:59] ‎Fulano criou este grupo\n
patterDH02= "^\[\d{2}\-\d{2}\-\d{2,4} \d{2}\:\d{2}\:\d{2}\]"  #[26-03-21 20:14:55] BENE...
DataSplit1= "-"
DataSplit2= "/"

marcaFone="\xa0"

def getChatAtrib(afilename):
    # coleta atributos do chat para o chatCatalog
    vetor= getProgramaGrupo(afilename) 
    posx= afilename.rfind("/")
    ofolder=""
    oarquivo= afilename
    if(posx > 0):
        ofolder= afilename[0:posx]
        oarquivo= afilename[posx+1:]
    vetor["folder"]= ofolder
    vetor["arquivo"]= oarquivo
    return(vetor)

# retorna datahora pattern do chat ou None
def getDataHoraPattern(datalist):
    for alinha in datalist:   
        pattern= patterDHY2
        m = re.search(pattern, alinha)
        if m is None:
            pattern= patterDHY4
            m = re.search(pattern, alinha)        
        if m is None:
            pattern= patterDHY2C
            m = re.search(pattern, alinha)
        if m is  None:
            pattern= patterDH01
            m = re.search(pattern, alinha)
        if m is  None:
            pattern= patterDH02
            m = re.search(pattern, alinha)        
        if m is  None:
            pattern= None
            continue
        break
    return(pattern)

def getPatternNaLinha(pattern, linha):
    m = re.search(pattern, linha)
    if m is None:
        return None
    stresult= m.group(0)
    return(stresult)
     
# identifica a parcela da data conforme seu valor máximo
def getsplitformat(max, pset):
    if '%m' not in pset and max  < 13 :
        return('%m')
    if '%d'not in pset and max < 32:
        return('%d')
    if max < 100:
        return('%y')
    return('%Y')

# identifica o formato da data no chat: %d/%m/%y %H:%M | %m/%d/%y %H:%M | %d/%m/%Y %H:%M
def getFormatDataHora(datalist, DataHoraPattern):
    # pattern de format da data
    i1max=0
    i2max=0
    i3max=0
    for alinha in datalist:
        adata= getLinhaDataHora(alinha, DataHoraPattern)
        if adata is None:
            continue
        adata= adata.replace("[","")
        adata= adata.replace("]","")
        sp1= adata.find(DataSplit1)
        if sp1 > 0:
            sp2= adata.find(DataSplit1, sp1+1)
            split= DataSplit1
        else:
            sp1= adata.find(DataSplit2)
            sp2= adata.find(DataSplit2, sp1+1)
            split= DataSplit2
        sp3= adata.find(" ", sp2+1)
        sp4= adata.find(":")   
        hms=""    
        if sp4 > 0:
            hms= " %H:%M"
            sp5= adata[sp4+1:].find(":")
            if sp5 > 0:
                hms= " %H:%M:%S"
        break
    for alinha in datalist:
        adata= getLinhaDataHora(alinha, DataHoraPattern)
        if adata is None:
            continue    
        adata= adata.replace("[","")
        adata= adata.replace("]","")
        x= adata[0:sp1]
        i1= int(x)
        if i1 > i1max:
            i1max=i1
        x= adata[sp1+1:sp2]
        i2= int(x)
        if i2 > i2max:
            i2max=i2
        x=adata[sp2+1:sp3]
        i3= int(x)
        if i3 > i3max:
            i3max=i3
    #  
    spat= set()
    i1pat= getsplitformat(i1max, spat)
    spat.add(i1pat)
    i2pat= getsplitformat(i2max, spat)
    spat.add(i2pat)
    i3pat= getsplitformat(i3max, spat)
    spat.add(i3pat)
    formato= i1pat+ split + i2pat + split + i3pat + hms
    return(formato)

# retorna strdata ou none
def getLinhaDataHora(linha, pattern):
    strdata= None
    linha= linha.replace("\u00a0"," ") 
    linha= linha.replace("\u200e","") 
    strdata= getPatternNaLinha(pattern, linha)
    return(strdata)

# retorna True/False
def checkIPHONE(linha):
    #[29/12/2018 21:09:59] ‎Fulano criou este grupo\n
    iphonedate1= "^\[\d{2}\/\d{2}\/\d{2,4} \d{2}\:\d{2}\:\d{2}\] "
    iphonedate2= "^\[\d{2}\-\d{2}\-\d{2,4} \d{2}\:\d{2}\:\d{2}\] "    
    m = re.search(iphonedate1, linha)
    res= m.group(0)
    strdata= res
    if(strdata is None):
        m = re.search(iphonedate2, linha)
        strdata= m.group(0)
        if(strdata is None):
            return (False)    
    return(True)

# retorna linha sem a data
def removeDataHora(strdata, linha):
    index= linha.find(strdata)
    if index < 0:
        return (linha)
    nova= linha.replace(strdata, "")
    first= nova[:1]
    if first=='-':
        nova= nova[1:]
    return(nova)

# getUtilFone: Extrai numero de telefone com multiplos padroes
def getUtilFone(linha):
    linha= linha.strip()
    # com menos de 8 caracters não é fone
    ntam= len(linha)
    if(ntam < 8):
        return(None)
    # sem números não é fone
    strdata= getPatternNaLinha("[0-9]+", linha)
    if strdata is None:
        return(None)
    # identifica fone conforme padrões    
    # pattern quebra galho para seguir com caso iphone
    patFone10="\+?\d{2}[\-\s]\d{2}[\-\s]\d{3,5}\S\d{3,5}"
    strdata= getPatternNaLinha(patFone10, linha)
    if strdata is None:
        # +1 (123) 456‑7890, "‪+1 (954) 612‑3012‬"
        patFone09="\+\d\s\(\d{1,3}\)\s\d{1,4}\s\d{1,4}"
        strdata= getPatternNaLinha(patFone09, linha)
        if strdata is None:
            patFone08="[\b\s\.+]?\d{8,14}[\b\s\.:,]" 
            strdata= getPatternNaLinha(patFone08, linha)
            if strdata is None:
                patFone07="[\b\s\.+]?\d{3,5}[- \.]\d{4,9}[:\s\.,]?"
                strdata= getPatternNaLinha(patFone07, linha)
                if strdata is None:
                    patFone06="[\b\s\.\(]\d{2}[\-\s\.\)]\d{4,5}[\-\s\.]\d{4}[\-\s\.]?"
                    strdata= getPatternNaLinha(patFone06, linha)
                    if strdata is None:
                        patFone05="[\b\s\.+]?\(?\d{1,3}\)?[\- \.]\d{3,5}[\- \.]\d{3,5}[:\s\.,]?"
                        strdata= getPatternNaLinha(patFone05, linha)
                        if strdata is None:
                            # (123) 456‑7890-123‬
                            patFone04="\(\d{1,3}\)(-?\s?\.?)\(?\d{1,3}\)?(-?\s?\.?)\d{2,5}(-?\s?\.?)\d{3,5}(-?\s?\.?:?,?)"
                            strdata= getPatternNaLinha(patFone04, linha)
                            if strdata is None:
                                # +55 87 8164-1749 , +55 21 98122 9332 
                                patFone03="(\b|\s|\.|\+|\D)\(?\d{2}\)?[\-\s\.]?\d{2,3}[\-\s\.]?\d{3,5}[\-\s\.]?\d{3,5}"
                                strdata= getPatternNaLinha(patFone03, linha)
                                if strdata is None:
                                    # *(31) 99778-9305*,  :87 9 81641749, 015.9.9730.6847
                                    patFone02="(\b|\s|\.|\D)\(?\d{1,3}\)?[\-\s\.]\d{1,5}[\-\s\.]\d{1,5}[\-\s\.]\d{1,5}"
                                    strdata= getPatternNaLinha(patFone02, linha)
                                    if strdata is None:
                                        patFone01="@\d{8,16}"   
                                        strdata= getPatternNaLinha(patFone01, linha)
                                        if strdata is None:
                                            return(None)
    return(strdata)

def clearFone(fone):
    if fone is not None:
        fone= fone.replace("\u00A0","")
        fone= fone.replace(marcaFone,"")    
        fone= fone.replace("@","")
        fone= fone.replace(":","")
        fone= fone.replace(".","")
        fone= fone.replace(",","")
        fone= fone.replace("(","")
        fone= fone.replace(")","")
        fone= fone.replace("-","")
        fone= fone.replace("+","")
        fone= fone.replace("*","")
        fone= fone.replace(" ","")
        fone= fone.replace("\n","")
    return(fone)
