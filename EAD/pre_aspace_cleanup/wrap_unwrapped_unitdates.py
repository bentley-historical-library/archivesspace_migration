from lxml import etree
import os
from os.path import join
import re

def wrap_unwrapped_unitdates(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	for filename in filenames:
		print "Wrapping unwrapped unitdates in {}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		unitdates = tree.xpath('//unitdate')
		rewrite = False
		resolved_unitdates = []
		for unitdate in unitdates:
			if unitdate not in resolved_unitdates:
				parent = unitdate.getparent()
				if parent.tag == "did":
					rewrite = True
					did_unitdates = parent.xpath('./unitdate')
					did_unitdates_elements = ["{0}--{1}--{2}".format(unitdate.get("type",""),unitdate.get("normal",""),unitdate.text.strip().encode('utf-8')) for unitdate in did_unitdates]
					unique_did_unitdates = set(did_unitdates_elements)
					new_unitdates = []
					for unitdate in unique_did_unitdates:
						elements = unitdate.split('--')
						new_unitdate = etree.Element("unitdate")
						if elements[0]:
							new_unitdate.attrib["type"] = elements[0]
						if elements[1]:
							new_unitdate.attrib["normal"] = elements[1]
						new_unitdate.text = elements[2]
						new_unitdates.append(new_unitdate)
					unittitles = parent.xpath('./unittitle')
					if unittitles:
						unittitle = unittitles[0]
						for unitdate in new_unitdates:
							unittitle.append(unitdate)
						unittitle_string = etree.tostring(unittitle)
						new_unittitle_string = re.sub(r"(\w)<u",r"\1 <u",unittitle_string.replace("><","> <"))
						new_unittitle = etree.fromstring(new_unittitle_string)
						parent.insert(parent.index(unittitle)+1,new_unittitle)
						parent.remove(unittitle)
					else:
						unittitle = etree.Element("unittitle")
						for unitdate in new_unitdates:
							unittitle.append(unitdate)
						parent.append(unittitle)
					for unitdate in did_unitdates:
						parent.remove(unitdate)
					resolved_unitdates.extend(unitdate for unitdate in did_unitdates)

		if rewrite:
			with open(join(ead_dir,filename),'w') as f:
				f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    wrap_unwrapped_unitdates(ead_dir)

if __name__ == "__main__":
    main()
