from lxml import etree
import re

def Compare(Reference, Filename):
    """Compares local XML file with FTP XML file"""
    #print("compare initia")
    try:
        if(isinstance(Reference,str) and isinstance(Filename,str)):
        # Parse the local file using lxml
            Local_Tree = etree.fromstring(Reference)
            Local_Root = Local_Tree
            Local_Tree = etree.ElementTree(Local_Root)
            
            # Parse the Machine File using lxml
            Machine_Tree = etree.fromstring(Filename)
            Machine_Root = Machine_Tree
            Machine_Tree = etree.ElementTree(Machine_Root)
        else:
            Local_Root = Reference
            Machine_Root = Filename
            Local_Tree = etree.ElementTree(Local_Root)
            Machine_Tree = etree.ElementTree(Machine_Root)
# I DONT HAVE ANY IDEA HOW IT ITERATES THROUGH ALL OF THE CHILDS BUT IT WORKS. DO NOT MOVE!!
        for element in Local_Root.iter():
            path = Local_Tree.getpath(element)
            Machine_Element = Machine_Root.xpath(path)
            if Machine_Element:
                Machine_Element = Machine_Element[0]
            else:
                Machine_Element = None
            if Machine_Element is not None:
                if element.text != Machine_Element.text:
                    print(f"Parent: {element.getparent()} Tag:{element.tag}, Machine Value: {Machine_Element.text} Local Value: {element.text}")
                    print(f"Line of mismatch: {element.sourceline}")
            else:
                break
        
    

    except etree.XMLSyntaxError as e:
        print(f"XML Syntax error: {e}")
        return False
    except Exception as e:
        print(f"Error occurred during comparison: {e}")
        return False
    
def main():
    print("program start")
    Local_File = "Movements.xml"
    Machine_File = "Movements_.xml"
    print("call of Compare")

    #GET THE FILE FROM FTP CONNECTION

    # OPEN THE XML FILE
    with open(Local_File, 'r', encoding='utf-8') as L:
        xml_content_L = L.read()

    # ESCAPE INVALID BRACHETS 
    xml_content_L = re.sub(r'<([^>]+)\[([^\]]+)\]>', r'<\1\2>', xml_content_L)

    with open(Machine_File, 'r', encoding='utf-8') as M:
        xml_content_M = M.read()

    # ESCAPE INVALID BRACHETS 
    xml_content_M = re.sub(r'<([^>]+)\[([^\]]+)\]>', r'<\1\2>', xml_content_M)

    Compare(xml_content_L, xml_content_M)


if __name__ == "__main__":
    main()

