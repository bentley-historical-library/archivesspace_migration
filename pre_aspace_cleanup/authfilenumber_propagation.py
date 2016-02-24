from lxml import etree
import os
from os.path import join

def build_text_to_authfilenumber_dict(ead_dir):
	print "Building text_to_authfilenumber_dict"
	special_cases = ['University of Michigan--Dearborn','University of Michigan--Flint','University of Michigan--Dearborn. Department of History','University of Wisconsin--Milwaukee','Lutheran Church--Missouri Synod']
	text_to_authfilenumber_dict = {}
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	for filename in filenames:
		tree = etree.parse(join(ead_dir,filename))
		for subject in tree.xpath('//controlaccess/*'):
			if subject.text and 'authfilenumber' in subject.attrib:
				subject_text = subject.text.strip().rstrip('.').encode('utf-8')
				if subject.tag in ['corpname','persname','famname'] and '--' in subject_text:
					subject_texts = subject_text.split('--')
					joined = '--'.join(subject_texts[0:2])
					if joined in special_cases:
						subject_text = joined
					else:
						subject_text = subject_texts[0]
				authfilenumber = subject.attrib['authfilenumber']
				if subject_text not in text_to_authfilenumber_dict:
					text_to_authfilenumber_dict[subject_text] = authfilenumber

	return text_to_authfilenumber_dict

def apply_authfilenumbers(text_to_authfilenumber_dict, ead_dir):
	special_cases = ['University of Michigan--Dearborn','University of Michigan--Flint','University of Michigan--Dearborn. Department of History','University of Wisconsin--Milwaukee','Lutheran Church--Missouri Synod']
	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
	for filename in filenames:
		print "Propagating authfilenumbers in {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		rewrite = False
		for subject in tree.xpath('//controlaccess/*'):
			if subject.text and not 'authfilenumber' in subject.attrib:
				subject_text = subject.text.strip().rstrip('.').encode('utf-8')
				if subject.tag in ['corpname','persname','famname'] and '--' in subject_text:
					subject_texts = subject_text.split('--')
					joined = '--'.join(subject_texts[0:2])
					if joined in special_cases:
						subject_text = joined
					else:
						subject_text = subject_texts[0]
				if subject_text in text_to_authfilenumber_dict:
					rewrite = True
					subject.attrib['authfilenumber'] = text_to_authfilenumber_dict[subject_text]
		if rewrite:
			with open(join(ead_dir,filename),'w') as f:
				f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def authfilenumber_propagation(ead_dir):
	text_to_authfilenumber_dict = build_text_to_authfilenumber_dict(ead_dir)
	apply_authfilenumbers(text_to_authfilenumber_dict, ead_dir)

def main():
	ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	authfilenumber_propagation(ead_dir)

if __name__ == "__main__":
	main()