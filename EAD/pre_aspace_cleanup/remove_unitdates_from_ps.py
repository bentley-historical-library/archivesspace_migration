from lxml import etree
import os
from os.path import join
import re

def remove_unitdates_from_ps(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	for filename in filenames:
		print "Removing unitdates from ps in {}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		unitdates = tree.xpath('//unitdate')
		rewrite = False
		ps_to_remove = []
		for unitdate in unitdates:
			parent = unitdate.getparent()
			if parent.tag == "p" and parent not in ps_to_remove:
				rewrite = True
				p_parent = parent.getparent()
				p_string = etree.tostring(parent)
				new_p_string = re.sub(r"<\/?unitdate.*?>","",p_string)
				new_p = etree.fromstring(new_p_string)
				p_parent.insert(p_parent.index(parent)+1,new_p)
				if parent not in ps_to_remove:
					ps_to_remove.append(parent)

		for p in ps_to_remove:
			p.getparent().remove(p)

		if rewrite:
			with open(join(ead_dir,filename),'w') as f:
				f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    remove_unitdates_from_ps(ead_dir)

if __name__ == "__main__":
    main()


