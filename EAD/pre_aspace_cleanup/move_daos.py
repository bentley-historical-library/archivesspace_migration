from lxml import etree
import os
from os.path import join

def move_daos(ead_dir):
    filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
    for filename in filenames:
        print "Moving daos in {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        daos = tree.xpath('//dao')
        rewrite = False
        for dao in daos:
            parent = dao.getparent()
            if parent.tag.startswith('c0'):
                rewrite = True
                parent_did = parent.xpath('./did')[0]
                parent_did.append(dao)
        if rewrite:
            with open(join(ead_dir,filename),'w') as ead_out:
                ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    move_daos(ead_dir)

if __name__ == "__main__":
    main()
