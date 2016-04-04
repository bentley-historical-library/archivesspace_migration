from lxml import etree
import os
from os.path import join
import re

def remove_nested_genreforms(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	removed_tags = {}
	for filename in filenames:
		print "Remove nested genreforms from physdesc subelements in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		physdesc_subelements = tree.xpath('//physfacet') + tree.xpath('//extent') + tree.xpath('//dimensions')
		rewrite = False
		for physdesc_subelement in physdesc_subelements:
			if physdesc_subelement.xpath('./*'):
				rewrite = True
				physdesc = physdesc_subelement.getparent()
				physdesc_subelement_tag = physdesc_subelement.tag
				for elem in physdesc_subelement.xpath('./*'):
					removed_tags[elem.tag] = removed_tags.get(elem.tag,0) + 1
				physdesc_subelement_string = etree.tostring(physdesc_subelement)
				physdesc_subelement_tags_removed = re.sub(r'<(.*?)>','',physdesc_subelement_string)
				physdesc_subelement_text = physdesc_subelement_tags_removed.strip()
				new_element = etree.Element(physdesc_subelement_tag)
				new_element.text = physdesc_subelement_text
				physdesc.insert(physdesc.index(physdesc_subelement)+1, new_element)
				physdesc.remove(physdesc_subelement)
		if rewrite:
			with open(join(ead_dir,filename),'w') as ead_out:
				ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))
	print removed_tags

def main():
	ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	remove_nested_genreforms(ead_dir)

if __name__ == "__main__":
	main()