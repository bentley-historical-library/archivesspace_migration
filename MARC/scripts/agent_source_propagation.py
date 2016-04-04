from lxml import etree
import os
from os.path import join
import re

def build_agent_source_dict(ead_dir):
	agent_sources = {}
	agent_tags = ["corpname", "famname", "persname"]
	for filename in os.listdir(ead_dir):
		print "Building agent sources from {}".format(filename)
		tree = etree.parse(join(ead_dir, filename))
		for agent in tree.xpath("//controlaccess/*"):
			if agent.tag in agent_tags:
				source = agent.get("source", "")
				agent_string = etree.tostring(agent)
				agent_string = re.sub(r"<(.*?)>", "", agent_string)
				if agent_string not in agent_sources:
					agent_sources[agent_string] = source

	return agent_sources


def propagate_agent_sources(ead_dir):
	agent_sources = build_agent_source_dict(ead_dir)

	for filename in os.listdir(ead_dir):
		print "Propagating agent sources in {}".format(filename)
		tree = etree.parse(join(ead_dir, filename))
		for agent in tree.xpath("//origination/*"):
			agent_string = etree.tostring(agent)
			agent_string = re.sub(r"<(.*?)>", "", agent_string)
			if agent_string in agent_sources:
				agent.attrib["source"] = agent_sources[agent_string]
			else:
				agent.attrib["source"] = "local"

		with open(join(ead_dir, filename), 'w') as f:
			f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))



def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	ead_dir = join(project_dir, "converted_eads")
	propagate_agent_sources(ead_dir)

if __name__ == "__main__":
	main()