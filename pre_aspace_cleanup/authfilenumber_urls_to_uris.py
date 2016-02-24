from lxml import etree
import os
from os.path import join

def authfilenumber_urls_to_uris(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	for filename in filenames:
		print "Changing authfilenumber urls to uris in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		rewrite = False
		for subject in tree.xpath('//controlaccess/*'):
			if 'authfilenumber' in subject.attrib:
				if subject.attrib['authfilenumber'].endswith('.html'):
					rewrite = True
					subject.attrib['authfilenumber'] = subject.attrib['authfilenumber'].replace('.html','')
		if rewrite:
			with open(join(ead_dir,filename),'w') as f:
				f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	authfilenumber_urls_to_uris(ead_dir)

if __name__ == "__main__":
	main()