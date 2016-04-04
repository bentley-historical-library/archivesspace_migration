import json
from lxml import etree
import os
from os.path import join
import re
import requests

def get_all_agents(ead_dir):
	agents = {"corpname":{}, "famname":{}, "persname":{}}

	agent_tags = ["corpname", "persname", "famname"]
	for filename in os.listdir(ead_dir):
		print "Extracting agents from {}".format(filename)
		tree = etree.parse(join(ead_dir, filename))
		for tag in agent_tags:
			for agent in tree.xpath("//{}".format(tag)):
				source = agent.attrib["source"]
				if source not in agents[tag]:
					agents[tag][source] = []
				for term in agent.xpath("./term"):
					agent.remove(term)
				agent_string = etree.tostring(agent).strip()
				agent_string = re.sub(r"<\/?{}(.*?)>".format(tag), "", agent_string).strip()
				if agent_string not in agents[tag][source]:
					agents[tag][source].append(agent_string)

	return agents

def make_agent_json(agents):
	print "Making agent json"
	agent_json = {"corpname":{}, "famname":{}, "persname":{}}

	for source in agents["corpname"]:
		for corpname in agents["corpname"][source]:
			corpname_json = make_corpname_json(corpname, source)
			agent_json["corpname"][corpname] = corpname_json

	for source in agents["famname"]:
		for famname in agents["famname"][source]:
			famname_json = make_famname_json(famname, source)
			agent_json["famname"][famname] = famname_json

	for source in agents["persname"]:
		for persname in agents["persname"][source]:
			persname_json = make_persname_json(persname, source)
			agent_json["persname"][persname] = persname_json

	return agent_json

def make_corpname_json(corpname, source):
	parsable_corpanme = etree.fromstring("<corpname>{}</corpname>".format(corpname))

	primary_name = parsable_corpanme.xpath("./primary_name")[0].text.strip()
	subordinate_name_1 = ""
	subordinate_name_2 = ""
	number = ""

	subordinate_names = []
	for subordinate_name in  parsable_corpanme.xpath("./subordinate_name"):
		subordinate_names.append(subordinate_name.text.strip())

	if subordinate_names:
		subordinate_name_1 = subordinate_names[0]
		if len(subordinate_names) > 1:
			subordinate_name_2 = ". ".join(subordinate_names[1:])

	if subordinate_name_2:
		subordinate_name_2, qualifier = extract_qualifier(subordinate_name_2)
	elif subordinate_name_1 and not subordinate_name_2:
		subordinate_name_1, qualifier = extract_qualifier(subordinate_name_1)
	elif not subordinate_name_1 and not subordinate_name_2:
		primary_name, qualifier = extract_qualifier(primary_name)

	if qualifier:
		qualifier = qualifier.strip(" ()")

	if parsable_corpanme.xpath("./number"):
		number = parsable_corpanme.xpath("./number")[0].text.strip()

	if not qualifier and len(qualifier.strip()) == 0:
		if subordinate_name_2 and len(subordinate_name_2.strip()) > 0 and not subordinate_name_2.endswith(')') and not subordinate_name_2.endswith('.'):
			subordinate_name_2 += '.'
		elif subordinate_name_1 and len(subordinate_name_1.strip()) > 0 and not subordinate_name_2 and not subordinate_name_1.endswith(')') and not subordinate_name_1.endswith('.'):
			subordinate_name_1 += '.'
		elif not subordinate_name_1 and not subordinate_name_2 and not primary_name.endswith(')') and not primary_name.endswith('.'):
			primary_name += '.'

	corpname_json = {u"names":[{u"primary_name":primary_name,
					u"subordinate_name_1":subordinate_name_1,
					u"subordinate_name_2":subordinate_name_2,
					u"qualifier":qualifier,
					u"number":number,
					u"source":source,
					u"sort_name_auto_generate":True}],
					u"publish":True}

	return corpname_json

def extract_qualifier(string):
	qualifier_regex = re.compile(r"(\([^\(]*?\))$")  # matches any ending parenthetical statement
	qualifier = ""

	qualifier_match = re.findall(qualifier_regex, string)
	if qualifier_match:
		qualifier = qualifier_match[-1]

	string = string.replace(qualifier, "").strip()

	return string, qualifier

def make_famname_json(famname, source):
	parsable_famname = etree.fromstring("<famname>{}</famname>".format(famname))

	family_name = parsable_famname.xpath("./family_name")[0].text.strip()
	qualifier = ""

	if parsable_famname.xpath("./qualifier"):
		qualifier = parsable_famname.xpath("./qualifier")[0].text.strip()

	if not qualifier:
		family_name, qualifier = extract_qualifier(family_name)

	if qualifier:
		qualifier = qualifier.strip(" ()")

	if not qualifier and not parsable_famname.xpath("./dates") and not family_name.endswith(".") and not family_name.endswith(")"):
		family_name += "."

	famname_json = {u"names":[{u"family_name":family_name,
					u"qualifier":qualifier,
					u"source":source,
					u"sort_name_auto_generate":True}],
					u"publish":True}

	if parsable_famname.xpath("./dates"):
		expression = parsable_famname.xpath("./dates")[0].text.strip()
		if "-" in expression:
			date_type = "range"
		else:
			date_type = "single"

		famname_json[u"dates_of_existence"] = [{u"label":u"existence",
												u"date_type":date_type,
												u"expression":expression}]

	return famname_json

def make_persname_json(persname, source):
	parsable_persname = etree.fromstring("<persname>{}</persname>".format(persname))

	primary_name = parsable_persname.xpath("./primary_name")[0].text.strip()
	rest_of_name = ""
	number = ""
	title = ""
	fuller_form = ""

	if parsable_persname.xpath("./rest_of_name"):
		if parsable_persname.xpath("./rest_of_name")[0].text:
			rest_of_name = parsable_persname.xpath("./rest_of_name")[0].text.strip()
	if parsable_persname.xpath("./number"):
		number = parsable_persname.xpath("./number")[0].text.strip()
	if parsable_persname.xpath("./title"):
		title = parsable_persname.xpath("./title")[0].text.strip()
	if parsable_persname.xpath("./fuller_form"):
		fuller_form = parsable_persname.xpath("./fuller_form")[0].text.strip(" ()")

	non_terminating_middle_initials = re.compile(r'\s[\.\s]?[A-Za-z]$')

	if non_terminating_middle_initials.search(rest_of_name) and not rest_of_name.endswith('.'):
		rest_of_name += "."

	if rest_of_name and not parsable_persname.xpath("./dates") and not title and not fuller_form and not number:
		if not rest_of_name.endswith('.'):
			rest_of_name += "."

	persname_json = {u"names":[{"primary_name":primary_name,
					u"rest_of_name":rest_of_name,
					u"title":title,
					u"fuller_form":fuller_form,
					u"number":number,
					u"source":source,
					u"name_order":u"inverted",
					u"sort_name_auto_generate":True}],
					u"publish":True}

	if parsable_persname.xpath("./dates") and parsable_persname.xpath("./dates")[0].text:
		expression = parsable_persname.xpath("./dates")[0].text.strip()
		if "-" in expression:
			date_type = "range"
		else:
			date_type = "single"

		persname_json[u"dates_of_existence"] = [{u"label":u"existence",
												u"date_type":date_type,
												u"expression":expression}]

	return persname_json

def post_agents(agent_json):
	agents_to_aspace_ids = {}

	auth = requests.post("http://localhost:8089/users/admin/login?password=admin").json()
	session = auth["session"]
	headers = {"X-ArchivesSpace-Session":session}

	for persname in agent_json["persname"]:
		aspace_json = agent_json["persname"][persname]
		response = requests.post("http://localhost:8089/agents/people", headers=headers, data=json.dumps(aspace_json)).json()
		agents_to_aspace_ids[persname] = extract_id(response)
		print response
	for corpname in agent_json["corpname"]:
		aspace_json = agent_json["corpname"][corpname]
		response = requests.post("http://localhost:8089/agents/corporate_entities", headers=headers, data=json.dumps(aspace_json)).json()
		agents_to_aspace_ids[corpname] = extract_id(response)
		print response
	for famname in agent_json["famname"]:
		aspace_json = agent_json["famname"][famname]
		response = requests.post("http://localhost:8089/agents/families", headers=headers, data=json.dumps(aspace_json)).json()
		agents_to_aspace_ids[famname] = extract_id(response)
		print response

	return agents_to_aspace_ids

def extract_id(response):
	if u"status" in response:
		aspace_id = response[u"uri"]

	if u"error" in response:
		aspace_id = response[u"error"][u"conflicting_record"][0]

	return aspace_id

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	ead_dir = join(project_dir, "converted_eads")
	agents_to_aspace_ids_file = join(project_dir, "agents_to_aspace_ids.json")
	agents = get_all_agents(ead_dir)
	agent_json = make_agent_json(agents)
	agents_to_aspace_ids = post_agents(agent_json)

	with open(agents_to_aspace_ids_file,"wb") as f:
		f.write(json.dumps(agents_to_aspace_ids))

if __name__ == "__main__":
	main()





