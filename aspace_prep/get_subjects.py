from lxml import etree
import csv
import os
from os.path import join


def get_subjects(ead_dir, subjects_agents_dir):
    tags = ['subject', 'geogname','genreform','title']
    subjects = {'subject':{},'geogname':{},'genreform':{},'title':{}}

    text_to_authfilenumber = {}

    unique_subject_csv = join(subjects_agents_dir, 'ead_unique_subjects.csv')
    text_to_authfilenumber_csv = join(subjects_agents_dir, 'text_to_authfilenumber.csv')

    for filename in os.listdir(ead_dir):
        print "Getting subjects from {0}".format(filename)
        tree = etree.parse(join(ead_dir, filename))
        for sub in tree.xpath('//controlaccess/*'):
            if sub.tag in tags and sub.text is not None:
                sub_text = sub.text.strip().encode('utf-8')
                source = sub.attrib['source']
                if source not in subjects[sub.tag]:
                    subjects[sub.tag][source] = []
                if sub_text not in subjects[sub.tag][source]:
                    subjects[sub.tag][source].append(sub_text)
                if 'authfilenumber' in sub.attrib:
                    authfilenumber = sub.attrib['authfilenumber']
                    if sub_text not in text_to_authfilenumber:
                        text_to_authfilenumber[sub_text] = authfilenumber
                        
    subject_data = []
    for subject_type in subjects:
        for source in subjects[subject_type]:
            for subject in subjects[subject_type][source]:
                row = []
                row.append(subject_type)
                row.append(source)
                row.append(subject)
                terms = subject.split('--')
                for term in terms:
                    row.append(term)
                subject_data.append(row)

    with open(unique_subject_csv,'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(subject_data)

    authfilenumber_data = []
    for subject_text in text_to_authfilenumber:
        row = [subject_text, text_to_authfilenumber[subject_text]]
        authfilenumber_data.append(row)

    with open(text_to_authfilenumber_csv,'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(authfilenumber_data)

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    subjects_agents_dir = join(project_dir,'subjects_agents')
    get_subjects(aspace_ead_dir, subjects_agents_dir)

if __name__ == "__main__":
    main()
