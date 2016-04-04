from lxml import etree
import os
from os.path import join

def find_missing_refs(ead_dir):
    tags = ['subject','geogname','genreform','title','persname','corpname','famname']
    missing_refs = {}
    for filename in os.listdir(ead_dir):
        print "Checking for missing refs in {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        for subject in tree.xpath('//controlaccess/*'):
            if subject.tag in tags and subject.text is not None:
                if not 'ref' in subject.attrib:
                    if 'subject' not in missing_refs:
                        missing_refs['subject'] = []
                    if filename not in missing_refs['subject']:
                        missing_refs['subject'].append(filename)
        for dao in tree.xpath('//dao'):
            if not 'ref' in dao.attrib:
                if 'dao' not in missing_refs:
                    missing_refs['dao'] = []
                if filename not in missing_refs['dao']:
                    missing_refs['dao'].append(filename)
        if not tree.xpath('//classification'):
            if 'classification' not in missing_refs:
                missing_refs['classification'] = []
            if filename not in missing_refs['classification']:
                missing_refs['classification'].append(filename)
    return missing_refs

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    find_missing_refs(aspace_ead_dir)

if __name__ == "__main__":
    main()