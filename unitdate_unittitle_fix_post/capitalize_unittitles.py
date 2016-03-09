from lxml import etree
import os
from os.path import join
import re

def capitalize_unittitles(ead_dir):
	for filename in os.listdir(ead_dir):
		print "Capitalizing unittitles in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		unittitles = tree.xpath('//did/unittitle')
		for unittitle in unittitles:
			if unittitle.text and len(unittitle.text.strip()) >= 1:
				unittitle_text = re.sub(r'^\s+','',unittitle.text)
				unittitle_text = re.sub(r'\s+',' ',unittitle_text)
				if not unittitle_text.startswith('de') and not unittitle_text.startswith('vs.') and not unittitle_text.startswith('von'):
					unittitle_text = unittitle_text[0].upper() + unittitle_text[1:]
				unittitle.text = unittitle_text
				if unittitle_text == '()' or unittitle_text == "[":
					unittitle.getparent().remove(unittitle)
		with open(join(ead_dir,filename),'w') as ead_out:
			ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	aspace_ead_dir = join(project_dir, 'eads')
	capitalize_unittitles(aspace_ead_dir)

if __name__ == "__main__":
	main()
