from lxml import etree
import os
from os.path import join
import csv

def update_posted_digital_objects(ead_dir, digital_objects_dir):

	digital_object_csv = join(digital_objects_dir, 'posted_digital_objects.csv')

	digital_object_refs = {}

	with open(digital_object_csv,'rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			dao_href = row[0]
			aspace_ref = row[1]
			digital_object_refs[dao_href] = aspace_ref

	for filename in os.listdir(ead_dir):
		print "Updating posted digital objects with uris in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		daos = tree.xpath('//dao')
		for dao in daos:
			if not 'ref' in dao.attrib:
				dao_href = dao.attrib['href'].strip()
				if dao_href in digital_object_refs:
					dao.attrib['ref'] = digital_object_refs[dao_href]

		with open(join(ead_dir,filename),'w') as ead_out:
			ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	aspace_ead_dir = join(project_dir, 'eads')
	digital_objects_dir = join(project_dir,'digital_objects')
	update_posted_digital_objects(aspace_ead_dir, digital_objects_dir)

if __name__ == "__main__":
	main()