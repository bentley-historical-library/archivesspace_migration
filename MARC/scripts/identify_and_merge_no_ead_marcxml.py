from lxml import etree
import os
from os.path import join
import shutil
import re

def make_directories(directories):
	for directory in directories:
		if not os.path.exists(directory):
			os.makedirs(directory)

def clear_directories(directories):
	for directory in directories:
		print "Deleting files from {}".format(directory)
		for filename in os.listdir(directory):
			os.remove(join(directory,filename))

def extract_ead_callnumbers_and_collectionids(ead_dir):
	ead_callnumbers = []
	ead_collectionids = []

	for filename in os.listdir(ead_dir):
		print "Extracting callnumbers and collectionids from {}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		callnumber = tree.xpath('//archdesc/did/unitid')[0].text.strip().encode('utf-8')
		eadid = tree.xpath('//eadid')[0].text.strip().encode('utf-8')
		collectionid = "-".join(eadid.split('-')[2:])
		if callnumber not in ead_callnumbers:
			ead_callnumbers.append(callnumber)
		if collectionid not in ead_collectionids:
			ead_collectionids.append(collectionid)

	return ead_callnumbers, ead_collectionids

def characterize_marcxmls(marcxml_dir, has_ead_dir, no_ead_dir, unknown_dir, ead_callnumbers, ead_collectionids):
	for filename in os.listdir(marcxml_dir):
		print "Characterizing {}".format(filename)
		ns = {'marc': 'http://www.loc.gov/MARC21/slim'}
		tree = etree.parse(join(marcxml_dir,filename))
		possible_ead_links = tree.xpath('//marc:datafield[@tag="856"]/marc:subfield[@code="u"]', namespaces=ns)
		callnumber = tree.xpath('//marc:datafield[@tag="852"]/marc:subfield[@code="h"]', namespaces=ns)
		has_ead_link = False
		if possible_ead_links:
			possible_ead_link_texts = [ead_link.text.strip().encode('utf-8') for ead_link in possible_ead_links]
			ead_link_texts = [ead_link for ead_link in possible_ead_link_texts if 'findaid' in ead_link]
			if ead_link_texts:
				has_ead_link = True
				ead_link_text = ead_link_texts[0]
				eadids = re.findall(r"umich\-bhl\-[\d\.\-]+|\d+$", ead_link_text)
				if eadids:
					eadid = eadids[0]
					if "-" in eadid:
						collectionid = "-".join(eadid.split('-')[2:])
					if collectionid in ead_collectionids and filename not in os.listdir(has_ead_dir):
						shutil.copy(join(marcxml_dir,filename),has_ead_dir)
					elif filename not in os.listdir(unknown_dir):
						shutil.copy(join(marcxml_dir,filename),unknown_dir)
				elif filename not in os.listdir(unknown_dir):
					shutil.copy(join(marcxml_dir,filename),unknown_dir)
		elif callnumber and not has_ead_link:
			callnumber_text = callnumber[0].text.strip().encode('utf-8')
			collectionid = False
			collectionids = re.findall(r"^[\d\.]+",callnumber_text)
			if collectionids:
				collectionid = collectionids[0]
			if callnumber_text in ead_callnumbers and filename not in os.listdir(has_ead_dir):
				shutil.copy(join(marcxml_dir,filename),has_ead_dir)
			elif collectionid and (collectionid in ead_collectionids or collectionid.startswith("87265")) and filename not in os.listdir(has_ead_dir):
				shutil.copy(join(marcxml_dir,filename),has_ead_dir)
			elif filename not in os.listdir(no_ead_dir):
				shutil.copy(join(marcxml_dir,filename),no_ead_dir)
		else:
			if filename not in os.listdir(unknown_dir):
				shutil.copy(join(marcxml_dir,filename),unknown_dir)

def merge_records(no_ead_dir, joined_dir):
	for filename in os.listdir(no_ead_dir):
		print "Merging MARC records - {}".format(filename)
		tree = etree.parse(join(no_ead_dir,filename))
		ns = {'marc': 'http://www.loc.gov/MARC21/slim'}
		record = tree.xpath('/marc:record',namespaces=ns)[0]
		call_number = tree.xpath('//marc:datafield[@tag="852"]/marc:subfield[@code="h"]', namespaces=ns)[0].text.strip().encode('utf-8')
		collection_id = re.findall(r"^\d+", call_number)[0]
		dst_filename = collection_id+".xml"
		if dst_filename not in os.listdir(joined_dir):
			collection = etree.Element("collection")
			collection.append(record)
			with open(join(joined_dir,dst_filename),'w') as f:
				f.write(etree.tostring(collection))
		else:
			existing_marc = etree.parse(join(joined_dir,dst_filename))
			collection = existing_marc.xpath('/collection')[0]
			collection.append(record)
			with open(join(joined_dir,dst_filename),'w') as f:
				f.write(etree.tostring(collection))

def main():
	ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	marcxml_dir = join(project_dir, 'marcxml_all')
	has_ead_dir = join(project_dir, 'marcxml_has_ead')
	no_ead_dir = join(project_dir, 'marcxml_no_ead')
	unknown_dir = join(project_dir, 'marcxml_unknown')
	joined_dir = join(project_dir, 'marcxml_no_ead_joined')

	make_directories([has_ead_dir, no_ead_dir, unknown_dir, joined_dir])
	clear_directories([has_ead_dir, no_ead_dir, unknown_dir, joined_dir])

	ead_callnumbers, ead_collectionids = extract_ead_callnumbers_and_collectionids(ead_dir)
	characterize_marcxmls(marcxml_dir, has_ead_dir, no_ead_dir, unknown_dir, ead_callnumbers, ead_collectionids)
	merge_records(no_ead_dir, joined_dir)

if __name__ == "__main__":
	main()