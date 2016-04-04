from lxml import etree
import csv
import os
from os.path import join

def get_compound_agents(ead_dir, subjects_agents_dir):
    tags = ['persname','corpname','famname']
    special_cases = ['University of Michigan--Dearborn','University of Michigan--Flint','University of Michigan--Dearborn. Department of History','University of Wisconsin--Milwaukee','Lutheran Church--Missouri Synod']
    uniques = []
    for filename in os.listdir(ead_dir):
        print "Extracting compound agents from {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        for agent in tree.xpath('//controlaccess/*'):
            if agent.tag in tags and agent.text is not None:
                agent_text = agent.text.strip().encode('utf-8')
                if '---' in agent_text:
                    agent_text = agent_text.replace('---','- --')
                if '--' in agent_text:
                    terms = agent_text.split('--')
                    joined = '--'.join(terms[0:2]).rstrip('.')
                    if joined in special_cases and len(terms) > 2 and agent_text not in uniques:
                        uniques.append(agent_text)
                    elif joined not in special_cases and agent_text not in uniques:
                        uniques.append(agent_text)

    data = []
    for unique in uniques:
        row = []
        row.append(unique)
        terms = unique.split('--')
        joined = '--'.join(terms[0:2])
        if joined in special_cases:
            row.append(joined)
            for term in terms[2:]:
                row.append(term)
        else:
            for term in terms:
                row.append(term)
        data.append(row)

    output_csv = join(subjects_agents_dir,'compound_agents.csv')

    with open(output_csv, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    subjects_agents_dir = join(project_dir,'subjects_agents')
    get_compound_agents(aspace_ead_dir, subjects_agents_dir)