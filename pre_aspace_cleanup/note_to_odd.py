from lxml import etree
import os
from os.path import join

def note_to_odd(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	for filename in filenames:
		print "Changing note to odd in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		notes = tree.xpath("//dsc//*[starts-with(local-name(), 'c0')]//note")
		if notes:
			for note in notes:
				note.tag = 'odd'
			with open(join(ead_dir,filename),'w') as f:
				f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))

def main():
	ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	note_to_odd(ead_dir)

if __name__ == "__main__":
	main()

