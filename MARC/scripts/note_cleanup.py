from lxml import etree
import os
from os.path import join

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
converted_eads = join(project_dir, 'converted_eads')

for filename in os.listdir(converted_eads):
	print filename
	tree = etree.parse(join(converted_eads, filename))
	odds = tree.xpath("//odd")
	for odd in odds:
		p = odd.xpath("./p")
		note_text = p[0].text.strip()
		if "donor" in note_text.lower():
			acqinfo = etree.Element("acqinfo")
			acqinfo.text = note_text
			odd_parent = odd.getparent()
			odd_parent.insert(odd_parent.index(odd)+1, acqinfo)
			odd_parent.remove(odd)
	extents = tree.xpath("//extent")
	for extent in extents:
		statement = extent.text.strip()
		if statement.startswith("ca"):
			statement = re.sub(r"^[A-Za-z]+\s","")
			extent.text = statement
	with open(join(converted_eads, filename), 'w') as f:
		f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))
