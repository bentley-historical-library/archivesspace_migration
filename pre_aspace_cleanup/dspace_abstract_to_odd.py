import urllib2
from lxml import etree
import urlparse
import os
from os.path import join
import time

def dspace_abstract_to_odd(ead_dir, dspace_mets_dir):
    skip = ['nispodcast.xml','bamdocs.xml','actonh.xml','stewartmary.xml','mullinsr.xml','pollackp.xml','saxj.xml','caen.xml','shurtleffm.xml','ticecarol.xml','ootbmpm.xml']
    add_odd = ['schoening.xml','nsfnet.xml','gonzalesjess.xml']
    filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
    for filename in filenames:
        print "Adding DSpace abstracts to odds in {0}".format(filename)
        if filename not in skip:
            tree = etree.parse(join(ead_dir, filename))
            rewrite = False
            daos = tree.xpath('//dao')
            for dao in daos:
                href = dao.attrib['href'].strip()
                did = dao.getparent()
                c = did.getparent()
                if href.startswith('http://hdl.handle.net/2027.42'):
                    if not did.xpath('./odd') and not c.xpath('./odd') or (filename in add_odd):
                        handlepath = urlparse.urlparse(href).path
                        the_id = handlepath.split('/')[-1]
                        if the_id + '.xml' in os.listdir(dspace_mets_dir):
                            metstree = etree.parse(join(dspace_mets_dir,the_id + '.xml'))
                            abstracts = metstree.xpath("//dim:field[@element='description'][@qualifier='abstract']", namespaces={'dim': 'http://www.dspace.org/xmlns/dspace/dim'})
                            if abstracts and abstracts[0].text:
                                print "Adding abstract from {0}".format(the_id)
                                rewrite = True
                                abstract = abstracts[0].text.encode('utf-8').decode('utf-8')
                                odd = etree.Element('odd')
                                ptag = etree.SubElement(odd,'p')
                                ptag.text = u"({0})".format(abstract.strip())
                                c.insert(c.index(did)+1, odd)
            if rewrite:
                with open(join(ead_dir,filename),'w') as f:
                    f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    dspace_mets_dir = 'C:/Users/djpillen/GitHub/dspace_mets'
    dspace_abstract_to_odd(ead_dir, dspace_mets_dir)

if __name__ == "__main__":
    main()