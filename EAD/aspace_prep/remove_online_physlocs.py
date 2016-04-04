from lxml import etree
import os
from os.path import join

def remove_online_physlocs(ead_dir):
	for filename in os.listdir(ead_dir):
		print "Removing <physloc>Online</physloc> from {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		physlocs = tree.xpath('//did/physloc')
		rewrite = False
		for physloc in physlocs:
			physloc_text = physloc.text.strip().encode('utf-8').lower()
			if physloc_text == 'online':
				rewrite = True
				physloc.getparent().remove(physloc)
		with open(join(ead_dir, filename),'w') as f:
			f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	aspace_ead_dir = join(project_dir, 'eads')
	remove_online_physlocs(aspace_ead_dir)

if __name__ == "__main__":
	main()

