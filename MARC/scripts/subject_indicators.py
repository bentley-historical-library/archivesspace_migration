from lxml import etree
import os
from os.path import join

subject_tags = ["630", "650", "651", "655", "656"]

marcxmls = "marcxml_no_ead"
ns = {'marc': 'http://www.loc.gov/MARC21/slim'}

tags_indicators = {}
for tag in subject_tags:
	tags_indicators[tag] = {}
tag_counts = {}

for marcxml in os.listdir(marcxmls):
	print marcxml
	tree = etree.parse(join(marcxmls, marcxml))
	records = tree.xpath("//marc:record", namespaces=ns)
	for record in records:
		for tag in subject_tags:
			subjects = record.xpath("./marc:datafield[@tag={}]".format(tag), namespaces=ns)
			for subject in subjects:
				tag_counts[tag] = tag_counts.get(tag, 0) + 1
				indicator = subject.get("ind2", "")
				if indicator not in tags_indicators[tag]:
					tags_indicators[tag][indicator] = 0
				tags_indicators[tag][indicator] += 1

for tag in tags_indicators:
	print tag, tag_counts[tag], tags_indicators[tag]
