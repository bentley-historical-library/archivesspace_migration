import os
from os.path import join
import re

def remove_and_between_dates(ead_dir):
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	for filename in filenames:
		print "Removing and between dates in {0}".format(filename)
		with open(join(ead_dir,filename),'r') as ead_in:
			full_text = ead_in.read()
		replaced = re.sub(r'</unitdate>\s?and\s?<unitdate',r'</unitdate>, <unitdate',full_text)
		with open(join(ead_dir,filename),'w') as ead_out:
			ead_out.write(replaced)

def main():
	ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	remove_and_between_dates(ead_dir)

if __name__ == "__main__":
	main()
