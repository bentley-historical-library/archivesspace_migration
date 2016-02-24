from lxml import etree
import csv
import os
from os.path import join
import re

ead_dir = 'eads'
ead_errors_csv = 'ead_verification_errors.csv'

tags = ['subject','geogname','genreform','title','persname','corpname','famname']

ead_errors = []

for filename in os.listdir(ead_dir):
	print "Checking for errors in {0}".format(filename)
	tree = etree.parse(join(ead_dir,filename))
	components = tree.xpath("//dsc//*[starts-with(local-name(), 'c0')]")
	classifications = tree.xpath('//classification')
	notes = tree.xpath('//scopecontent') + tree.xpath('//odd') + tree.xpath('//abstract')
	for note in notes:
		note_text = re.sub(r'<(.*?)','',etree.tostring(note)).strip().encode('utf-8')
		if not note_text:
			ead_errors.append([filename,'missing note content',tree.getpath(note)])
	if not classifications:
		ead_errors.append([filename, 'missing classification'])
	for subject in tree.xpath('//controlaccess/*'):
		if subject.tag in tags and subject.text is not None:
			if not 'ref' in subject.attrib:
				ead_errors.append([filename,subject.tag + ' missing ref',tree.getpath(subject)])
	for dao in tree.xpath('//dao'):
		if not 'ref' in dao.attrib:
			ead_errors.append([filename, 'dao missing ref',tree.getpath(dao)])
	for component in components:
		unittitles = component.xpath('./did/unittitle')
		unitdates = component.xpath('./did/unitdate')
		containers = component.xpath('./did/container')
		if unittitles:
			unittitle = re.sub(r'<(.*?)>','',etree.tostring(unittitles[0])).strip().encode('utf-8')
			if not unittitle:
				ead_errors.append([filename, 'empty unittitle',tree.getpath(component)])
		elif not unitdates:
			ead_errors.append([filename, 'missing a title and/or date',tree.getpath(component)])
		if containers:
			top_container = containers[0]
			if not top_container.text:
				ead_errors.append([filename, 'container missing indicator',tree.getpath(component)])
			if 'label' in top_container.attrib:
				if not '[' in top_container.attrib['label']:
					ead_errors.append([filename,'container missing barcode',tree.getpath(component)])
			else:
				ead_errors.append([filename, 'container missing label',tree.getpath(component)])
			if not 'type' in top_container.attrib:
				ead_errors.append([filename,'container missing type',tree.getpath(component)])
			if len(containers) == 2:
				top_container = containers[0]
				sub_container = containers[1]
				if not 'id' in top_container.attrib:
					ead_errors.append([filename,'parent container missing id',tree.getpath(component)])
				if not 'parent' in sub_container.attrib:
					ead_errors.append([filename, 'child container missing parent',tree.getpath(component)])
				if 'id' in top_container.attrib and 'parent' in sub_container.attrib:
					if top_container.attrib['id'] != sub_container.attrib['parent']:
						ead_errors.append([filename, 'mismatching container id and parent values',tree.getpath(component)])

with open(ead_errors_csv,'wb') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerows(ead_errors)


