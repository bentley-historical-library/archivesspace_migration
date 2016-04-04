import lxml
from lxml import etree
import xml.etree.cElementTree as cElementTree
import os
from os.path import join

def split_marcxml_exports(exports, dst_dir):
    counter = 0
    for export in exports:
        tree = etree.iterparse(export)
        context = iter(tree)
        event, root = context.next()
        for event, elem in context:
            if event == "end":
                if elem.tag == '{http://www.loc.gov/MARC21/slim}record':
                    elem.tail = None
                    counter += 1
                    filename = str(counter)
                    while len(filename) < 5:
                        filename = '0' + filename
                    with open(join(dst_dir, filename+'.xml'),'w') as marc_out:
                        marc_out.write(etree.tostring(elem, encoding="utf-8", xml_declaration=True, pretty_print=True))
                    print filename

if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dst_dir = join(project_dir, 'marcxml_all')
    marcxml_basedir = 'C:/Users/djpillen/GitHub/marc_xml-all/mlibrary_exports'
    marcxml_has_ead = join(marcxml_basedir, 'bent_marc_has_ead.xml')
    marcxml_no_ead = join(marcxml_basedir, 'bent_marc_no_ead.xml')
    exports = [marcxml_has_ead, marcxml_no_ead]
    split_marcxml_exports(exports, dst_dir)
