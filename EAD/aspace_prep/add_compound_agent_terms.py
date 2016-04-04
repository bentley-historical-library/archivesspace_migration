import csv
from lxml import etree
import os
from os.path import join

def add_compound_agent_terms(ead_dir, subjects_agents_dir):
    compound_agent_terms = join(subjects_agents_dir, 'compound_agents_terms.csv')

    compound_agent_terms_dict = {}
    term_type_dict = {}

    tags = ['corpname','persname','famname']

    with open (compound_agent_terms,'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            row_index = len(row) - 1
            index = 1
            agent = row[0]
            compound_agent_terms_dict[agent] = []
            while index < row_index:
                term = row[index]
                term_type = row[index+1]
                compound_agent_terms_dict[agent].append(term)
                term_type_dict[term] = term_type
                index += 2

    for filename in os.listdir(ead_dir):
        print "Splitting subdivided agent terms in {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        for agent in tree.xpath('//controlaccess/*'):
            if agent.tag in tags:
                agent_text = agent.text.strip().encode('utf-8')
                if '---' in agent_text:
                    agent_text = agent_text.replace('---','- --')
                if agent_text in compound_agent_terms_dict:
                    for term in compound_agent_terms_dict[agent_text]:
                        new_term = etree.Element('term')
                        new_term.text = term
                        new_term.attrib['type'] = term_type_dict[term]
                        agent.append(new_term)
        with open(join(ead_dir,filename),'w') as ead_out:
            ead_out.write(etree.tostring(tree,xml_declaration=True,encoding='utf-8',pretty_print=True))

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    subjects_agents_dir = join(project_dir,'subjects_agents')
    add_compound_agent_terms(aspace_ead_dir, subjects_agents_dir)

if __name__ == "__main__":
    main()
