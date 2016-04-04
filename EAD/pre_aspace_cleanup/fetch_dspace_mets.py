import urllib2
from lxml import etree
import urlparse
import os
from os.path import join
import time

def fetch_dspace_mets(ead_dir, dspace_mets_dir):
    print "Fetching DSpace METS"
    filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
    for filename in filenames:
        tree = etree.parse(join(ead_dir,filename))
        daos = tree.xpath('//dao')
        for dao in daos:
            href = dao.attrib['href'].strip()
            if href.startswith('http://hdl.handle.net/2027.42'):
                handlepath = urlparse.urlparse(href).path
                the_id = handlepath.split('/')[-1]
                if the_id + '.xml' not in os.listdir(dspace_mets_dir):
                    mets = "http://deepblue.lib.umich.edu/metadata/handle" + handlepath + "/mets.xml"
                    print "Fetching {0}".format(mets)
                    page = urllib2.urlopen(mets)
                    metstree = etree.parse(page)
                    with open(join(dspace_mets_dir, the_id + '.xml'),'w') as mets_out:
                        mets_out.write(etree.tostring(metstree))
                    time.sleep(15)

def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    dspace_mets_dir = 'C:/Users/djpillen/GitHub/dspace_mets'
    fetch_dspace_mets(ead_dir, dspace_mets_dir)

if __name__ == "__main__":
    main()
