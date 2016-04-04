from lxml import etree
import os
from os.path import join

def camelcase_attributes(aspace_ead_dir):
	for filename in os.listdir(aspace_ead_dir):
		print "Camelcasing dao attributes in {0}".format(filename)
		tree = etree.parse(join(aspace_ead_dir,filename))
		daos = tree.xpath('//dao')
		for dao in daos:
			if 'actuate' in dao.attrib:
				if dao.attrib['actuate'] == 'onrequest':
					dao.attrib['actuate'] = 'onRequest'
				elif dao.attrib['actuate'] == 'onload':
					dao.attrib['actuate'] = 'onLoad'
		with open(join(aspace_ead_dir,filename),'w') as ead_out:
			ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	aspace_ead_dir = join(project_dir, 'eads')
	camelcase_attributes(aspace_ead_dir)

if __name__ == "__main__":
	main()