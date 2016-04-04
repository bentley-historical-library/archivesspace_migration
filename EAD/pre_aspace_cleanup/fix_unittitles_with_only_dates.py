from lxml import etree
import os
from os.path import join
import re

def fix_unittitles_with_only_dates(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith(".xml")]
	for filename in filenames:
		print "Fixing wonky unitdate display in unittitles with only unitdates in {}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		components = tree.xpath("//dsc//*[starts-with(local-name(), 'c0')]")
		for component in components:
			did = component.xpath('./did')[0]
			unittitle = did.xpath('./unittitle')[0]
			whitespace_regex = r"\s{2,}|\v|\n|\r"
			new_unittitle_string = " ".join(re.split(whitespace_regex, etree.tostring(unittitle)))
			new_unittitle_string = new_unittitle_string.replace("</unitdate> <unitdate","</unitdate>, <unitdate").replace("<unittitle> ","<unittitle>").replace(" </unittitle>","</unittitle>")
			new_unittitle = etree.fromstring(new_unittitle_string)
			did.insert(did.index(unittitle)+1, new_unittitle)
			did.remove(unittitle)

		with open(join(ead_dir,filename),'w') as f:
			f.write(etree.tostring(tree, encoding="utf-8",xml_declaration=True,pretty_print=True))

def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    fix_unittitles_with_only_dates(ead_dir)

if __name__ == "__main__":
    main()