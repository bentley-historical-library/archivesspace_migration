import csv
from lxml import etree
import os
from os.path import join
import re

def make_beal_classifications_dict(beal_classifications):
	collection_types = {}
	faculty_collections = []

	with open(beal_classifications,'rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			collectionid = row[0].strip()
			collection_type = row[1].strip()
			if collectionid and collection_type:
				collection_types[collectionid] = collection_type.lower()
				faculty_collection = row[2]
				if faculty_collection:
					faculty_collections.append(collectionid)

	return collection_types, faculty_collections

def add_classifications(ead_dir, beal_classifications):
	classification_base = '/repositories/2/classifications/'
	mhc_classification = classification_base + '1'
	uarp_classification = classification_base + '2'
	faculty_classification = classification_base + '3'

	collection_types, faculty_collections = make_beal_classifications_dict(beal_classifications)

	for filename in os.listdir(ead_dir):
		print "Adding classifications to {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		eadheader = tree.xpath('//eadheader')[0]


		call_number = tree.xpath("//archdesc/did/unitid")[0].text.strip().encode("utf-8")
		call_number_collectionids = re.findall(r"^\d+", call_number)
		collectionid_call_number = ""
		if call_number_collectionids:
			collectionid_call_number = call_number_collectionids[0]

		if collectionid_call_number and collectionid_call_number in collection_types:
			collection_type = collection_types[collectionid_call_number]
		else:
			collection_type = False

		if collectionid_call_number in faculty_collections:
			faculty_collection = True
		else:
			faculty_collection = False

		classification_ids = []

		if collection_type:
			if collection_type == "mhc":
				classification_ids.append(mhc_classification)
			elif collection_type in ["uarp", "ua"]:
				classification_ids.append(uarp_classification)

		if faculty_collection:
			classification_ids.append(faculty_classification)
		
		for classification_id in classification_ids:
			classification = etree.Element('classification')
			classification.attrib['ref'] = classification_id
			eadheader.append(classification)

		with open(join(ead_dir,filename),'w') as ead_out:
			ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	ead_dir = join(project_dir, 'converted_eads')
	beal_classifications = join(project_dir, "beal_classifications.csv")
	add_classifications(ead_dir, beal_classifications)

if __name__ == "__main__":
	main()