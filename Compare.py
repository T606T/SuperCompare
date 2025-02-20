from lxml import etree
import re
from ftplib import FTP,error_perm
import paramiko
import tkinter as tk
from tkinter import filedialog
import sys

def open_file_explorer():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path

def Compare(Local, Machine):
    """Compares local XML file with FTP XML file"""
    ErrorLines = []
    #print("compare initia")
    try:
        if(isinstance(Local,str) and isinstance(Machine,str)):
            # Parse the local file using lxml
            try:
                Local_Root = etree.fromstring(Local)
                Machine_Root = etree.fromstring(Machine)
            except etree.XMLSyntaxError as e:
                print(f"XML Parsing error: {e}")
                print("Ensure that the input XML strings are formatted right.")
                return False
            Local_Tree = etree.ElementTree(Local_Root)
            Machine_Tree = etree.ElementTree(Machine_Root)

        else:
            Local_Tree = etree.ElementTree(Local)
            Local_Root = Local_Tree.getroot()
            Machine_Tree = etree.ElementTree(Machine)
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
                #print(f"Parent: {element.getparent()} Tag:{element.tag}, Machine Value: {Machine_Element.text} Local Value: {element.text}")
                #print(f"Line of mismatch: {element.sourceline}")
                ErrorLines.append(element.sourceline)

        print(f"ErrorLines: {ErrorLines}")
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
def SFTP_GETFILE(SFTP_Host, Filename):
    port = 20022
    username = "+++++++++"
    password = "+++++++++"
    Client = paramiko.SSHClient()
    Client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Accept unknown keys from machine
    try:
        Client.connect(SFTP_Host,port,username,password)
        SFTP = Client.open_sftp()
        #ASK FOR LOCAL FILE
        #tkinter.Tk().withdraw()
        Local_File = open_file_explorer() #xml reference in local machine
        if Local_File:
           print("Selected file:",Local_File)
        else:
            print("No file selected")
        # OPEN THE XML FILE
        with open(Local_File, 'r', encoding='utf-8') as L:
            xml_content_L = L.read()
         # ESCAPE INVALID BRACHETS 
        xml_content_L = re.sub(r'<([^>]+)\[([^\]]+)\]>', r'<\1\2>', xml_content_L)

        #GET FILE FROM Machine
        #Check if the D: drive is accessible
        try:
            File_Directory = 'Config/' #Get Directory from USER
            SFTP.chdir(File_Directory)
        except Exception as e:
            print(f"Failed to access {File_Directory}", str(e))
            sys.exit(1)
        #GET FILE    
        with SFTP.open(Filename,mode='r') as M:
            xml_content_M = M.read().decode('utf-8')
        # ESCAPE INVALID BRACHETS 
        xml_content_M = re.sub(r'<([^>]+)\[([^\]]+)\]>', r'<\1\2>', xml_content_M)

        #COMPARE FILES
        Compare(xml_content_L,xml_content_M)
        SFTP.close()
        

    except paramiko.AuthenticationException:
        print("Authentication failed. Check your username/password.")
    except paramiko.SSHException as e:
        print(f"SSH connection error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        Client.close()
        print("Connection closed.")


      
def main():
    print("program start")
    #CONNECT TO THE MACHINE BIA FTP
    File = "example.xml" #Local File name
    IP = "++++++++" #GET A WORKING IP ADDRESS
    Machine_File = SFTP_GETFILE(IP,File)
    Fleet = 3
    for i in range(Fleet): 
        #COMPARE FILES AND INCREASE IP address

    #SFTP_GETFILE(IP)

    #GET THE FILE FROM FTP CONNECTION

    

   # with open(Machine_File, 'r', encoding='utf-8') as M:
    

    #Compare(xml_content_L, xml_content_M)


if __name__ == "__main__":
    main()

