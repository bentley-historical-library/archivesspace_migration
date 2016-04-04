from lxml import etree
import os
from os.path import join

def identify_problem_eads(ead_dir):
	for filename in os.listdir(ead_dir):
		tree = etree.parse(join(ead_dir, filename))
		dsc = tree.xpath("//dsc")
		if not dsc:
			note_texts = " ".join([odd.text for odd in tree.xpath("//odd/p")])
			if "separately" in note_texts:
				print filename

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	ead_dir = join(project_dir, 'converted_eads')
	identify_problem_eads(ead_dir)

if __name__ == "__main__":
	main()