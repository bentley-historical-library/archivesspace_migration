import json
from lxml import etree
import os
from os.path import join
import re
import requests

def get_subjects(ead_dir):
	subjects = {}

	for filename in os.listdir(ead_dir):
		print "Getting subjects from {}".format(filename)
		tree = etree.parse(join(ead_dir, filename))
		for subject in tree.xpath("//subject"):
			if subject.xpath("./term"):
				source = normalize_source(subject.attrib["source"])
				if source not in subjects:
					subjects[source] = []
				subject_string = etree.tostring(subject)
				subject_string = re.sub(r"<\/?subject(.*?)>","", subject_string)
				if subject_string not in subjects[source]:
					subjects[source].append(subject_string)

	return subjects

def make_subjects_json(subjects):
	subjects_json = {}
	print "Making subjects json"
	for source in subjects:
		for subject in subjects[source]:
			parsable_subject = etree.fromstring("<subject>{}</subject>".format(subject))
			terms_list = []
			for term in parsable_subject.xpath("./term"):
				term_dict = {}
				term_dict["term_type"] = term.attrib["type"]
				term_dict["term"] = term.text.strip()
				term_dict["vocabulary"] = "/vocabularies/1"
				terms_list.append(term_dict)

			subject_json = {u"source":source,
							u"vocabulary":"/vocabularies/1",
							u"terms":[term for term in terms_list]}

			subjects_json[subject] = subject_json

	return subjects_json

def normalize_source(source):
	if source in ["ltcgm", "lctrgm", "lcgtm", "1ctgm", "lctm"]:
		source = "lctgm"

	if source in ["1csh"]:
		source = "lcsh"

	return source.strip(".").strip("]")

def post_subjects(subjects_json):
	subjects_to_aspace_ids = {}

	auth = requests.post("http://localhost:8089/users/admin/login?password=admin").json()
	session = auth["session"]
	headers = {"X-ArchivesSpace-Session":session}

	for subject in subjects_json:
		subject_json = subjects_json[subject]
		response = requests.post("http://localhost:8089/subjects", headers=headers, data=json.dumps(subject_json)).json()
		print response
		subjects_to_aspace_ids[subject] = extract_id(response)

	return subjects_to_aspace_ids

def extract_id(response):
	if u"status" in response:
		aspace_id = response[u"uri"]
	if u"error" in response:
		aspace_id = response[u"error"][u"conflicting_record"][0]

	return aspace_id

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	ead_dir = join(project_dir, "converted_eads")
	subjects_to_aspace_ids_file = join(project_dir, "subjects_to_aspace_ids.json")
	subjects = get_subjects(ead_dir)
	subjects_json = make_subjects_json(subjects)
	subjects_to_aspace_ids = post_subjects(subjects_json)

	with open(subjects_to_aspace_ids_file,"wb") as f:
		f.write(json.dumps(subjects_to_aspace_ids))

if __name__ == "__main__":
	main()






