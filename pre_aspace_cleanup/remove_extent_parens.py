from lxml import etree
import os
from os.path import join
import re

def remove_extent_parens(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	for filename in filenames:
		print "Remove parens from extents in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		extents = tree.xpath('//extent')
		rewrite = False
		for extent in extents:
			if extent.text:
				extent_text = extent.text.strip().encode('utf-8')
				if extent_text.startswith('(') and extent_text.endswith(')'):
					rewrite = True
					extent_text_modified = re.sub(r'^\(|\)$','',extent_text)
					extent.text = extent_text_modified
		if rewrite:
			with open(join(ead_dir,filename),'w') as ead_out:
				ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	remove_extent_parens(ead_dir)

if __name__ == "__main__":
	main()