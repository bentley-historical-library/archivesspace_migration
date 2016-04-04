import json
from lxml import etree
import os
from os.path import join
import re

def add_uris(subject_to_aspace_id_map, agent_to_aspace_id_map, ead_dir):
	agent_tags = ["corpname", "persname", "famname"]
	for filename in os.listdir(ead_dir):
		print "Adding subject and agent refs to {}".format(filename)
		tree = etree.parse(join(ead_dir, filename))
		for subject in tree.xpath("//subject"):
			if subject.xpath("./term"):
				subject_string = etree.tostring(subject)
				subject_string = re.sub(r"<\/?subject(.*?)>", "", subject_string)
				subject.attrib["ref"] = subject_to_aspace_id_map[subject_string]
			else:
				subject.getparent().remove(subject)
		for tag in agent_tags:
			for agent in tree.xpath("//{}".format(tag)):
				agent_string = etree.tostring(agent).strip()
				agent_string = re.sub(r"<\/?{}(.*?)>".format(tag), "", agent_string).strip()
				agent_string = re.sub(r"<term(.*?)>(.*?)<\/term>", "", agent_string).strip()
				agent.attrib["ref"] = agent_to_aspace_id_map[agent_string]

		with open(join(ead_dir, filename), 'w') as f:
			f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))


def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	ead_dir = join(project_dir, "converted_eads")
	subject_to_aspace_id_map = json.load(open(join(project_dir, "subjects_to_aspace_ids.json")))
	agent_to_aspace_id_map = json.load(open(join(project_dir, "agents_to_aspace_ids.json")))
	add_uris(subject_to_aspace_id_map, agent_to_aspace_id_map, ead_dir)

if __name__ == "__main__":
	main()

