from lxml import etree
import re
from ftplib import FTP, error_perm
import paramiko
import tkinter as tk
from tkinter import filedialog
import sys

def open_file_explorer():
    """Opens a file explorer dialog and returns the selected file path."""
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename()

def Compare(local_xml, machine_xml):
    """Compares local XML file with remote XML file and returns differing lines."""
    error_lines = []

    try:
        if isinstance(local_xml, str) and isinstance(machine_xml, str):
            try:
                local_root = etree.fromstring(local_xml)
                machine_root = etree.fromstring(machine_xml)
            except etree.XMLSyntaxError as e:
                print(f"XML Parsing error: {e}")
                print("Ensure that the input XML strings are properly formatted.")
                return False
        else:
            local_tree = etree.ElementTree(local_xml)
            local_root = local_tree.getroot()
            machine_tree = etree.ElementTree(machine_xml)
            machine_root = machine_tree.getroot()

        for element in local_root.iter():
            path = f"{local_root.tag}/{element.tag}"
            machine_element = machine_root.xpath(path)
            if machine_element:
                machine_element = machine_element[0]
            else:
                continue

            if element.text != machine_element.text:
                error_lines.append(element.sourceline)

        print(f"Mismatch found at lines: {error_lines}")
        return error_lines

    except etree.XMLSyntaxError as e:
        print(f"XML Syntax error: {e}")
        return False
    except Exception as e:
        print(f"Error during comparison: {e}")
        return False

def GetFile(ftp_host):
    """Retrieves a file from an FTP server."""
    ftp_user = ""
    ftp_pass = ""

    try:
        ftp = FTP(timeout=10)
        ftp.connect(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_pass)
        print("Connected to FTP server.")

        # Get directory from user
        directory = input("Enter the directory of the target file: ")
        ftp.cwd(directory)
        print("Files in the directory:")
        ftp.retrlines('LIST')

        file_name = input("Enter the file name: ")
        file_content = []

        def handle_binary(data):
            file_content.append(data.decode('utf-8'))

        ftp.retrbinary(f"RETR {file_name}", handle_binary)
        print(f"File '{file_name}' retrieved successfully.")

        ftp.quit()
        return ''.join(file_content)

    except error_perm as e:
        print(f"Directory '{directory}' is invalid or inaccessible. Error: {e}")
        ftp.quit()
        return None
    except Exception as e:
        print(f"FTP error: {e}")
        return None

def SFTP_GETFILE(SFTP_Host, Filename):
    """Connects to an SFTP server, retrieves an XML file, and compares it with a local file."""
    port = 20022
    username = "+++++++++"
    password = "+++++++++"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(SFTP_Host, port, username, password)
        sftp = client.open_sftp()

        # Ask for local file
        local_file = open_file_explorer()
        if not local_file:
            print("No file selected.")
            return

        print(f"Selected file: {local_file}")

        # Read the local file
        with open(local_file, 'r', encoding='utf-8') as f:
            xml_content_local = f.read()

        # Escape invalid brackets
        xml_content_local = re.sub(r'<([^>]+)\[([^\]]+)\]>', r'<\1\2>', xml_content_local)

        # Change directory and retrieve the remote file
        remote_directory = 'Config/'

        try:
            sftp.chdir(remote_directory)
        except Exception as e:
            print(f"Failed to access {remote_directory}: {e}")
            sys.exit(1)

        with sftp.open(Filename, 'r') as remote_file:
            xml_content_machine = remote_file.read().decode('utf-8')

        # Escape invalid brackets
        xml_content_machine = re.sub(r'<([^>]+)\[([^\]]+)\]>', r'<\1\2>', xml_content_machine)

        # Compare the two XML files
        Compare(xml_content_local, xml_content_machine)

    except paramiko.AuthenticationException:
        print("Authentication failed. Check your username/password.")
    except paramiko.SSHException as e:
        print(f"SSH connection error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        client.close()
        print("SFTP connection closed.")

def main():
    """Main function to iterate over IP addresses and fetch files via SFTP."""
    print("Program started.")

    # Root IP address (change this to a real IP)
    root_ip = "192.168.1.10"

    # Extract and increment last segment of the IP address
    ip_parts = root_ip.split('.')
    last_segment = int(ip_parts[-1])
    fleet_size = 15

    for i in range(fleet_size):
        ip_parts[-1] = str(last_segment + i)
        new_hostname = '.'.join(ip_parts)

        # Compare files and iterate over IP addresses
        file_name = "example.xml"
        SFTP_GETFILE(new_hostname, file_name)

if __name__ == "__main__":
    main()
