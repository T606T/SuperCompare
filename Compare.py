from lxml import etree
import re
from ftplib import FTP,error_perm
import paramiko 

def Compare(Reference, Filename):
    """Compares local XML file with FTP XML file"""
    #print("compare initia")
    try:
        if(isinstance(Reference,str) and isinstance(Filename,str)):
            # Parse the local file using lxml
            try:
                Local_Root = etree.fromstring(Reference)
                Machine_Root = etree.fromstring(Filename)
            except etree.XMLSyntaxError as e:
                print(f"XML Parsing error: {e}")
                print("Ensure that the input XML strings are formatted right.")
                return False
            Local_Tree = etree.ElementTree(Local_Root)
            Machine_Tree = etree.ElementTree(Machine_Root)

        else:
            Local_Tree = etree.ElementTree(Reference)
            Local_Root = Local_Tree.getroot()
            Machine_Tree = etree.ElementTree(Filename)
            Machine_Root = Machine_Tree.getroot()
# FIX COMPARE FUNCTION
        for element in Local_Root.iter():
            path = Local_Tree.getpath(element)
            Machine_Element = Machine_Root.xpath(path)
            if Machine_Element:
                Machine_Element = Machine_Element[0]
            else:
                Machine_Element = None
                continue
            if element.text != Machine_Element.text:
                print(f"Parent: {element.getparent()} Tag:{element.tag}, Machine Value: {Machine_Element.text} Local Value: {element.text}")
                print(f"Line of mismatch: {element.sourceline}")

    except etree.XMLSyntaxError as e:
        print(f"XML Syntax error: {e}")
        return False
    except Exception as e:
        print(f"Error occurred during comparison: {e}")
        return False
def GetFile(ftp_host):
    # FTP connection credentials
    ftp_user = ""
    ftp_pass = ""
    ftp = FTP(timeout=10)
    ftp.connect(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_pass)
    print("Connected to FTP server.")

    # Get to the directory of the file
    Dir = input("State the Directory of target file: ")
    try:
        #EN VEZ DE SELECCIONAR EL ARCHIVO EN EL SERVIDOR, SERIA MEJOR SELECCIONAR EL ARCHIVO LOCAL Y HACER MATCH POR NOMBRE CON LOS ARCHIVOS DE LAS MAQUINAS. ASI SE EVITA EL FIRSTFILE Y DESPUËS COMPARAR TODOS LOS DEMAS.
        ftp.cwd(Dir)
        print("Files on the server:")
        ftp.retrlines('LIST')  # List files in the directory

        File = input("Select file: ")
        file_content = []

        # Retrieve the file content as a string
        def handle_binary(data):
            file_content.append(data.decode('utf-8'))

        ftp.retrbinary(f"RETR {File}", handle_binary)
        print(f"File '{File}' read successfully from the server.")
        content = ''.join(file_content)  # Return the file content as a string
        ftp.quit()
        return content

    except error_perm as e:
        print(f"Directory '{Dir}' is invalid or inaccessible. Error: {e}")
        ftp.quit()
        return None
def SFTP_GETFILE(SFTP_Host):
    Client = paramiko.SFTPClient(22)
    Directory = Client.getcwd
    print(f"Here is the Current Directory: {Directory}")

      
def main():
    print("program start")
    #CONNECT TO THE MACHINE BIA FTP
    IP_Address = "IP_Address" # Add MAchine IP
    Local_File = "Filename"#Local File name
    Machine_File = GetFile(IP_Address)
    IP = "127.0.0.1" #GET A WORKING IP ADDRESS

    SFTP_GETFILE(IP)

    #GET THE FILE FROM FTP CONNECTION

    # OPEN THE XML FILE
    with open(Local_File, 'r', encoding='utf-8') as L:
        xml_content_L = L.read()

    # ESCAPE INVALID BRACHETS 
    xml_content_L = re.sub(r'<([^>]+)\[([^\]]+)\]>', r'<\1\2>', xml_content_L)

   # with open(Machine_File, 'r', encoding='utf-8') as M:
    xml_content_M = Machine_File

    # ESCAPE INVALID BRACHETS 
    xml_content_M = re.sub(r'<([^>]+)\[([^\]]+)\]>', r'<\1\2>', xml_content_M)

    #Compare(xml_content_L, xml_content_M)


if __name__ == "__main__":
    main()

