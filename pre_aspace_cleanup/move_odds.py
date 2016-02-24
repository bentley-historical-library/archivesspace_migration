from lxml import etree
import os
from os.path import join

def move_odds(ead_dir):
    filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
    for filename in filenames:
        print "Moving odds in {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        didodds = tree.xpath("//dsc//*[starts-with(local-name(), 'c0')]//did/odd")
        if didodds:
            for didodd in didodds:
                did = didodd.getparent()
                c = did.getparent()
                c.insert(c.index(did)+1, didodd)
            with open(join(ead_dir,filename),'w') as f:
                f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True,pretty_print=True))

def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    move_odds(ead_dir)

if __name__ == "__main__":
    main()