from lxml import etree
import os
from os.path import join
import re

def skip_nested_items(ead_dir):
	for filename in os.listdir(ead_dir):
		print "Skipping nested lists in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		items = tree.xpath('//item')
		lists = tree.xpath('//list')
		rewrite = False
		for top_list in lists:
			if len(re.findall('list', tree.getpath(top_list))) == 1:
				sublists = top_list.xpath('.//list')
				if sublists:
					rewrite = True
					for sublist in sublists:
						sublist.tag = 'sublist'
		for item in items:
			subitems = item.xpath('.//item')
			if subitems:
				rewrite = True
				for subitem in subitems:
					subitem.tag = 'subitem'
		if rewrite:
			with open(join(ead_dir,filename),'w') as ead_out:
				ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	# Replace this with the path to your eads
	aspace_ead_dir = join(project_dir, 'eads')
	skip_nested_items(aspace_ead_dir)

if __name__ == "__main__":
	main()