from lxml import etree
import os
from os.path import join

ns = {'marc': 'http://www.loc.gov/MARC21/slim'}


marcxml_dir = "marcxml_no_ead_joined"

no_main_record = []
for filename in os.listdir(marcxml_dir):
	print filename
	tree = etree.parse(join(marcxml_dir, filename))
	records = tree.xpath("//marc:record", namespaces=ns)
	if len(records) > 1:
		five80s = tree.xpath("//marc:datafield[@tag='580']", namespaces=ns)
		seven73s = tree.xpath("//marc:datafield[@tag='773']", namespaces=ns)
		LKRs = tree.xpath("//marc:datafield[@tag='LKR']", namespaces=ns)

		if (len(records) - len(five80s) != 1) and (len(records) - len(seven73s) != 1) and (len(records) - len(LKRs) != 1):
			no_main_record.append(filename)

print "Unid main records: ", no_main_record
