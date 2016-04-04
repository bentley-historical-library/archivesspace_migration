from lxml import etree
import os
from os.path import join

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
converted_eads = join(project_dir, "converted_eads")

for filename in os.listdir(converted_eads):
	print filename
	tree = etree.parse(join(converted_eads, filename))
	archdesc = tree.xpath("//archdesc")[0]
	controlaccesses = tree.xpath("//controlaccess")
	insertion_point = archdesc.index(controlaccesses[0])
	new_controlaccess_elements = []
	for controlaccess in controlaccesses:
		for subject_elem in controlaccess.xpath("./*"):
			subject = etree.tostring(subject_elem)
			if subject not in new_controlaccess_elements:
				new_controlaccess_elements.append(subject)
		controlaccess.getparent().remove(controlaccess)

	new_controlaccess = etree.Element("controlaccess")
	for element in new_controlaccess_elements:
		new_element = etree.fromstring(element)
		new_controlaccess.append(new_element)
		
	archdesc.insert(insertion_point, new_controlaccess)

	with open(join(converted_eads, filename), 'w') as f:
		f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))