import csv
from lxml import etree
import os
from os.path import join
from datetime import datetime

def remove_expired_restrictions(ead_dir):
    filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
    now = datetime.now().strftime("%Y-%m-%d")
    for filename in filenames:
        print "Removing expired restrictions in {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        accessrestricts = tree.xpath('//accessrestrict')
        rewrite = False
        for accessrestrict in accessrestricts:
            dates = accessrestrict.xpath('./p/date')
            if dates:
                date = dates[0]
                if 'normal' in date.attrib:
                    normalized = date.attrib['normal']
                    if normalized < now:
                        accessrestrict.getparent().remove(accessrestrict)
        if rewrite:
            with open(join(ead_dir,filename),'w') as f:
                f.write(etree.tostring(tree,encoding='utf-8',pretty_print=True,xml_declaration=True))


def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    remove_expired_restrictions(ead_dir)

if __name__ == "__main__":
    main()