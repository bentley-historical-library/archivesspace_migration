import csv
from lxml import etree
import os
from os.path import join
import re

def make_ead_collectionids_list(ead_path):
	ead_collectionids = []
	filenames = [filename for filename in os.listdir(ead_path)]
	for filename in filenames:
		tree = etree.parse(join(ead_path,filename))
		eadid = tree.xpath('//eadid')[0].text.strip().encode('utf-8')
		collectionid_eadid = eadid.split('-')[-1]
		ead_collectionids.append(collectionid_eadid)
		callnumber = tree.xpath('//archdesc/did/unitid')[0].text.strip().encode('utf-8')
		collectionid_callnumbers = re.findall(r"^\d+",callnumber)
		if collectionid_callnumbers:
			collectionid_callnumber = collectionid_callnumbers[0]
			if collectionid_callnumber not in ead_collectionids:
				ead_collectionids.append(collectionid_callnumber)

	return ead_collectionids


def make_beal_collectionids_list(locations_csv):
	beal_collectionids = []

	with open(locations_csv,'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			collectionid = row.get("collection_id","")
			if collectionid not in beal_collectionids:
				beal_collectionids.append(collectionid)

	return beal_collectionids

def make_marc_collectionids_list(marc_path):
	marc_collectionids = []
	filenames = [filename for filename in os.listdir(marc_path)]
	for filename in filenames:
		ns = {'marc': 'http://www.loc.gov/MARC21/slim'}
		tree = etree.parse(join(marc_path,filename))
		callnumber = tree.xpath('//marc:datafield[@tag="852"]/marc:subfield[@code="h"]', namespaces=ns)[0].text.strip().encode('utf-8')
		collectionids = re.findall(r"^\d+",callnumber)
		if collectionids:
			collectionid = collectionids[0]
			if collectionid not in marc_collectionids:
				marc_collectionids.append(collectionid)

	return marc_collectionids

def make_unique_beal_collectionids_list(beal_collectionids, ead_collectionids, marc_collectionids):
	unique_beal_collectionids = [collectionid for collectionid in beal_collectionids if collectionid not in ead_collectionids+marc_collectionids]
	return unique_beal_collectionids

def write_unique_collectionids_to_document(unique_collectionids_list, unique_collectionids_document):
	with open(unique_collectionids_document,'w') as f:
		f.write("\n".join(unique_collectionids_list))


def main():
	ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	marc_dir = 'marcxml_no_ead'
	locations_csv = 'C:/Users/djpillen/GitHub/barcoding/locations.csv'
	unique_collectionids_document = "beal_unique_collectionids.txt"
	ead_collectionids = make_ead_collectionids_list(ead_dir)
	marc_collectionsids = make_marc_collectionids_list(marc_dir)
	beal_collectionids = make_beal_collectionids_list(locations_csv)
	unique_beal_collectionids = make_unique_beal_collectionids_list(beal_collectionids, ead_collectionids, marc_collectionsids)
	write_unique_collectionids_to_document(unique_beal_collectionids, unique_collectionids_document)

if __name__ == "__main__":
	main()

