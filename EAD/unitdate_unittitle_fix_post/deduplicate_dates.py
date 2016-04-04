from lxml import etree
import os
from os.path import join
import re

def remove_duplicate_unitdates(ead_dir):
	for filename in os.listdir(ead_dir):
		print "Removing duplicate unitdates in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		components = tree.xpath("//dsc//*[starts-with(local-name(), 'c0')]")
		rewrite = False
		for component in components:
			unitdates = component.xpath('./did/unitdate')
			if unitdates:
				unitdates_normal = []
				unitdates_expression = []
				for unitdate in unitdates:
					normal = unitdate.get("normal","")
					expression = unitdate.text.strip().encode('utf-8')
					if normal:
						if normal not in unitdates_normal and expression not in unitdates_expression:
							unitdates_normal.append(normal)
							unitdates_expression.append(expression)
						else:
							unitdate.getparent().remove(unitdate)
							rewrite = True
		if rewrite:
			with open(join(ead_dir,filename),'w') as f:
				f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def consolidate_duplicate_data(ead_dir):
	for filename in os.listdir(ead_dir):
		print "Consolidating unitdate data in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		unittitles = tree.xpath('//did/unittitle')
		rewrite = False
		for unittitle in unittitles:
			if 'altrender' in unittitle.attrib and unittitle.attrib['altrender'] == 'calcified':
				rewrite = True
				del unittitle.attrib['altrender']
				did = unittitle.getparent()
				unitdates = did.xpath('./unitdate')
				inclusive_ranges = []
				bulk_ranges = []
				non_normalized = {}
				for unitdate in unitdates:
					normal = unitdate.get('normal','')
					date_type = unitdate.get('type','')
					if normal:
						dates = normal.split('/')
						if date_type == "inclusive":
							inclusive_ranges.extend([date.split('-')[0] for date in dates])
						elif date_type == "bulk":
							bulk_ranges.extend([date.split('-')[0] for date in dates])
						else:
							inclusive_ranges.extend([date.split('-')[0] for date in dates])
					else:
						date = unitdate.text.strip().encode('utf-8')
						non_normalized[date] = date_type
					did.remove(unitdate)
				if inclusive_ranges:
					new_unitdate = etree.Element("unitdate")
					new_unitdate.attrib["type"] = "inclusive"
					if len(set(inclusive_ranges)) >= 2:
						new_unitdate.attrib["normal"] = "{0}/{1}".format(min(inclusive_ranges), max(inclusive_ranges))
						new_unitdate_text = "{0}-{1}".format(min(inclusive_ranges), max(inclusive_ranges))
						new_unitdate.text = new_unitdate_text
					elif len(set(inclusive_ranges)) == 1:
						new_unitdate.attrib["normal"] = "{0}".format(inclusive_ranges[0])
						new_unitdate_text = "{0}".format(inclusive_ranges[0])
						new_unitdate.text = new_unitdate_text
					did.append(new_unitdate)
				if bulk_ranges:
					new_unitdate = etree.Element("unitdate")
					new_unitdate.attrib["type"] = "bulk"
					if len(set(bulk_ranges)) >= 2:
						new_unitdate.attrib["normal"] = "{0}/{1}".format(min(bulk_ranges), max(bulk_ranges))
						new_unitdate_text = "{0}-{1}".format(min(bulk_ranges), max(bulk_ranges))
						new_unitdate.text = new_unitdate_text
					elif len(set(bulk_ranges)) == 1:
						new_unitdate.attrib["normal"] = "{0}".format(bulk_ranges[0])
						new_unitdate_text = "{0}".format(bulk_ranges[0])
						new_unitdate.text = new_unitdate_text
					did.append(new_unitdate)
				if non_normalized:
					for date in non_normalized:
						new_unitdate = etree.Element("unitdate")
						new_unitdate.attrib["type"] = non_normalized[date]
						new_unitdate.text = date
						did.append(new_unitdate)
		if rewrite:
			with open(join(ead_dir,filename),'w') as f:
				f.write(etree.tostring(tree,encoding="utf-8",xml_declaration=True,pretty_print=True))




def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	aspace_ead_dir = join(project_dir, 'eads')
	#remove_duplicate_unitdates(aspace_ead_dir)
	consolidate_duplicate_data(aspace_ead_dir)

if __name__ == "__main__":
	main()