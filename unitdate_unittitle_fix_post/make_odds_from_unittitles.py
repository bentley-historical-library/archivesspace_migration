from lxml import etree
import os
from os.path import join
import re

def make_odds_from_unittitles(ead_dir):
	for filename in os.listdir(ead_dir):
		print "Making <odd>s from unittitles in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		components = tree.xpath("//dsc//*[starts-with(local-name(), 'c0')]")
		rewrite = False
		for component in components:
			if component.xpath('./did/unittitle') and component.xpath('./did/unitdate'):
				unittitle = component.xpath('./did/unittitle')[0]
				if unittitle.text:
					unittitle_text = unittitle.text.strip().encode('utf-8')
					if unittitle_text.startswith('(') and unittitle_text.endswith(')') and len(re.findall(r'[\(\)]',unittitle_text)) == 2:
						rewrite = True
						new_odd = etree.Element('odd')
						new_p = etree.SubElement(new_odd,'p')
						new_p.text = unittitle_text
						did = unittitle.getparent()
						component.insert(component.index(did)+1,new_odd)
						did.remove(unittitle)
		if rewrite:
			with open(join(ead_dir,filename),'w') as f:
				f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	aspace_ead_dir = join(project_dir, 'eads')
	make_odds_from_unittitles(aspace_ead_dir)

if __name__ == "__main__":
	main()