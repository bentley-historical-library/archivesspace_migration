from lxml import etree
import os
from os.path import join
import re

def fix_collection_level_unittitle_commas(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith(".xml")]
	for filename in filenames:
		print "Removing collection level unittitle/unitdate commas in {}".format(filename)
		tree = etree.parse(join(ead_dir, filename))
		collection_unittitle = tree.xpath('//archdesc/did/unittitle')[0]
		if "," in etree.tostring(collection_unittitle):
			new_collection_unittitle_string = re.sub(r"</unitdate>[,\s]*<unitdate","</unitdate> <unitdate",etree.tostring(collection_unittitle))
			new_collection_unittitle = etree.fromstring(new_collection_unittitle_string)
			parent = collection_unittitle.getparent()
			parent.insert(parent.index(collection_unittitle)+1, new_collection_unittitle)
			parent.remove(collection_unittitle)

			with open(join(ead_dir,filename), 'w') as f:
				f.write(etree.tostring(tree, encoding="utf-8",xml_declaration=True, pretty_print=True))

def main():
	ead_dir = 'D:/github/vandura/Real_Masters_all'
	fix_collection_level_unittitle_commas(ead_dir)

if __name__ == "__main__":
	main()

