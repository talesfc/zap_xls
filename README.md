# ZAP_XLS - a python script that builds an excel compatible file from a text file exported from whatsapp.

# WhatsApp chat text file exporting
Current procedure for exporting chat files is as follows:

1. Export chat file from WhatsApp on mobile device:
    a- click on 3 dots mark on top right menu
    b- select menu option "More"
    c- select next menu option "Export chat"
    d- choose one of 2 options for export: include media files | no media files
    e- wait and wait ... depending on your choice & mobile resources, it may take a long time or not finish
    f- choose option for sharing exported file, ex: email

2. Recover exported file from email and save where convenient as zip file 

3. Use zip tool of choice to extract embedded .txt file and save on folder: ...zap_xls/data/txt_files

4. Change file name so as to enclose with a underscore mark the name you want to use as the chat name, example: 'WhatsApp chat  example - _A chat 4 you_.txt'

# Chat file content format
The input chat file contains a set of text lines of two different types:

a- A formatted text line divided in 3 parts: first is the datetime, second is the participant identification (by name or phone number), third part is a free text field. Datetime and participant are separated by a ' - ' character, while participant and free text fields are separated by a ' : ' character, as in the example:
"30/04/2022 08:31 - +55 79 98XX-XXXX: Abençoado Sábado para todos nós."

b- A unformatted free text line, as in the example: "Obrigada a todos pelo carinho e pelo apoio."

c- In addition, following applies:
- the participant field content is usually defined by the phone number of a chat group participant. However, if this number happens to be registered in the device contacts app, it will be replaced by the person full name registered in the contacts app

- datetime format depends on device type/model (ex: IOS, Android) and device localization configurations. Five datetime formats are considered: dd/MM/yy hh:mm, dd/MM/yyyy hh:mm, MM/dd/yy, hh:mm, dd/MM/yyyy hh:mm:ss, dd-MM-yyyy hh:mm:ss 

- depending on device, some special text markers (such as "\u200E" and "<U\\+200E>") may also be used as separators between the fields in the formatted text line. 

# Chat file content description
Each text line in the file may represent one of two types of content: a chat event or a chat post message content.

- Chat events are always defined by a single line formatted text where the free text field contains information on the chat event type.

- Chat posts always start by a single line formatted text, composed by datetime and participant identification, as described above, followed by free text field containg the message content. For short text messages the single line may be sufficient for the full post content. For larger text messages, the single formatted line is followed by a set of free text lines. For image and video content, a text pointer is provided for the location of the midia file.

# How to use
1- Put one or multiple input text files in ./files_txt_in folder with "txt" extension
2- Run script "ImportChat_from_File.py" located in zap_xls root folder. No parameters are needed.
3- Output xlsx files files will be created with xlsx extension and same name as input files, in folder: ./files_xlsx_out 
4- After processing, input text files will be moved to folder: ./files_txt_out
