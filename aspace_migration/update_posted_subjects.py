from lxml import etree
import os
from os.path import join
import csv

def update_posted_subjects(ead_dir, subjects_agents_dir):
    posted_subjects_csv = join(subjects_agents_dir, 'posted_subjects.csv')

    posted_subjects = {'geogname':{},'genreform':{},'subject':{},'title':{}}

    tags = ['geogname','genreform','subject','title']

    with open(posted_subjects_csv,'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            tag = row[0]
            source = row[1]
            subject = row[2]
            uri = row[-1]
            if source not in posted_subjects[tag]:
                posted_subjects[tag][source] = {}
            posted_subjects[tag][source][subject] = uri

    for filename in os.listdir(ead_dir):
        print "Adding subject uris to {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        for sub in tree.xpath('//controlaccess/*'):
            if sub.tag in tags and sub.text is not None and not 'ref' in sub.attrib:
                tag = sub.tag
                source = sub.attrib['source']
                subject = sub.text.strip().encode('utf-8')
                if subject in posted_subjects[tag][source]:
                    sub.attrib['ref'] = posted_subjects[tag][source][subject]

        with open(join(ead_dir,filename),'w') as ead_out:
            ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    subjects_agents_dir = join(project_dir,'subjects_agents')
    update_posted_subjects(aspace_ead_dir, subjects_agents_dir)

if __name__ == "__main__":
    main()
