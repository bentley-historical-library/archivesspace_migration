from lxml.builder import E
from lxml import etree
import os
from os.path import join
import shutil
import uuid

ns = {'marc': 'http://www.loc.gov/MARC21/slim'}

def identify_main_record(records):
	# Use some combination of looking for LKR and 580 and 773 fields to find the "main record"
	# The main record will not have a LKR, 580, or 773 field
	main_record_identified = False
	records_count = len(records)
	five80s_count = 0
	seven73s_count = 0
	LKRs_count = 0
	main_records = []
	other_records = []
	for record in records:
		five80s = record.xpath("./marc:datafield[@tag='580']", namespaces=ns)
		five80s_count += len(five80s)
		seven73s = record.xpath("./marc:datafield[@tag='773']", namespaces=ns)
		seven73s_count += len(seven73s)
		LKRs = record.xpath("./marc:datafield[@tag='LKR']", namespaces=ns)
		LKRs_count += len(LKRs)
		if five80s or seven73s or LKRs:
			other_records.append(record)
		else:
			main_records.append(record)

	if (len(main_records) == 1) and (len(main_records) + len(other_records) == records_count):
		return main_records[0], other_records
	else:
		return False, False


def make_eadheader(record):
	eadheader = E.eadheader(
		make_filedesc(record),
		make_profiledesc(record)
		)

	return eadheader

def make_filedesc(record):
	filedesc = E.filedesc(
		E.titlestmt(
			make_titleproper(record),
			make_sponsor(record)
			)
		)

	return filedesc

def make_titleproper(record):
	titleproper = "Finding aid for the " + extract_collection_title(record)

	return E.titleproper(titleproper)

def make_sponsor(record):
	sponsor = record.xpath("./marc:datafield[@tag='536']/marc:subfield[@code='a']", namespaces=ns)

	if sponsor:
		return E.sponsor(sponsor[0].text.strip())
	else:
		return ""

def make_profiledesc(record):
	profiledesc = E.profiledesc(
		E.creation("Encoded finding aid created from MARC record by Dallas Pillen"),
		E.langusage("The finding aid is written in ", E.language({"langcode":"eng"},"English")),
		make_descrules(record)
		)

	return profiledesc

def make_descrules(record):
	descrules = record.xpath("./marc:datafield[@tag='040']/marc:subfield[@code='e']", namespaces=ns)

	if descrules:
		return E.descrules(descrules[0].text.strip())
	else:
		return ""

def make_archdesc(record):
	archdesc = E.archdesc({"level":"collection"},
		make_collection_did(record),
		make_descgrp(record),
		make_bioghist(record),
		make_arrangement(record),
		make_scopecontent(record),
		make_controlaccess([record])
		)

	return archdesc

def make_collection_did(record):
	did = E.did(
		make_unitid(record),
		make_origination(record),
		make_unittitle(record),
		make_langmaterial(record),
		)

	unitdates = make_unitdates(record, "collection")
	for unitdate in unitdates:
		did.append(unitdate)

	physdescs = make_physdescs(record)
	for physdesc in physdescs:
		did.append(physdesc)

	return did


def make_unitid(record):
	call_number = record.xpath("./marc:datafield[@tag='852']/marc:subfield[@code='h']", 
										namespaces=ns)

	mirlyn_record = record.xpath("./marc:controlfield[@tag='001']", namespaces=ns)

	if call_number:
		unitid = E.unitid(call_number[0].text.strip())
	elif mirlyn_record:
		unitid = E.unitid("NO CALL NUMBER -- {}".format(mirlyn_record[0].text.strip()))
	else:
		unitid = E.unitid("NO CALL NUMBER -- {}".format(uuid.uuid4()))

	return unitid

def make_origination(record):

	person_creator = record.xpath("./marc:datafield[@tag='100'][@ind1='1']", namespaces=ns)
	family_creator = record.xpath("./marc:datafield[@tag='100'][@ind1='3']", namespaces=ns)
	corp_creator = record.xpath("./marc:datafield[@tag='110']", namespaces=ns) + record.xpath("./marc:datafield[@tag='111']", namespaces=ns)

	if person_creator:
		return E.origination(make_persname(person_creator[0], "origination"))
	elif family_creator:
		return E.origination(make_famname(family_creator[0], "origination"))
	elif corp_creator:
		return E.origination(make_corpname(corp_creator[0], "origination"))
	else:
		return ""

def make_unittitle(record):
	return E.unittitle(extract_collection_title(record))

def make_langmaterial(record):
	langmaterials = record.xpath("./marc:datafield[@tag='546']", namespaces=ns)

	if langmaterials:
		langmaterial = langmaterials[0]
		language_note = langmaterial.xpath("./marc:subfield[@code='a']", namespaces=ns)[0].text.strip()
		materials_specified = langmaterial.xpath("./marc:subfield[@code='3']", namespaces=ns)
		if materials_specified:
			language_note += ": {}".format(materials_specified[0].text.strip())

		return E.langmaterial(language_note)
	else:
		return ""

def make_unitdates(record, level):
	unitdates = []

	inclusive_dates = record.xpath("./marc:datafield[@tag='245']/marc:subfield[@code='f']", namespaces=ns)
	bulk_dates = record.xpath("./marc:datafield[@tag='245']/marc:subfield[@code='g']", namespaces=ns)
	publication_dates = record.xpath("./marc:datafield[@tag='260']/marc:subfield[@code='c']", namespaces=ns)

	if inclusive_dates or bulk_dates:
		for inclusive_date in inclusive_dates:
			unitdates.append(make_unitdate(inclusive_date, "creation", "inclusive"))
		for bulk_date in bulk_dates:
			unitdates.append(make_unitdate(bulk_date, "creation", "bulk"))
	elif publication_dates:
		for publication_date in publication_dates:
			unitdates.append(make_unitdate(publication_date, "creation", "inclusive"))
	elif level == "collection":
		unitdates.append(E.unitdate("[No date provided]"))

	return unitdates

def make_unitdate(unitdate, date_label, date_type):
	expression = unitdate.text.strip().rstrip(".")
	
	return E.unitdate({"label":date_label,"type":date_type}, expression)

def extract_collection_title(record):
	title_section = record.xpath("./marc:datafield[@tag='245']",namespaces=ns)[0]

	"""
	main_title = title_section.xpath("./marc:subfield[@code='a']", namespaces=ns)
	subtitle = title_section.xpath("./marc:subfield[@code='b']", namespaces=ns)
	responsibility = title_section.xpath("./marc:subfield[@code='c']", namespaces=ns)
	medium = title_section.xpath("./marc:subfield[@code='h']", namespaces=ns)
	number_of_part = title_section.xpath("./marc:subfield[@code='n']", namespaces=ns)
	name_of_part = title_section.xpath("./marc:subfield[@code='p']", namespaces=ns))

	collection_title = main_title[0].text.strip()
	collection_title += " " + subtitle[0].text.strip() if subtitle else ""
	collection_title += " {}".format(medium[0].text.strip()) if medium else ""
	collection_title += " {}".format(number_of_part[0].text.strip()) if number_of_part else ""
	collection_title += " {}".format(name_of_part[0].text.strip()) if name_of_part else ""
	collection_title += "/ " + responsibility[0].text.strip() if responsibility else ""
	"""

	title_codes = ["a","b","c","h","n","p"]
	collection_title = ""
	for subfield in title_section.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in title_codes:
			collection_title += " " + subfield.text.strip()

	return collection_title.strip().rstrip(",")

def make_physdescs(record):
	physdescs = []
	physdesc_elements = record.xpath("./marc:datafield[@tag='300']", namespaces=ns) + record.xpath("./marc:datafield[@tag='305']", namespaces=ns) + record.xpath("./marc:datafield[@tag='516']", namespaces=ns)

	if physdesc_elements:
		for physdesc in physdesc_elements:
			physdescs.append(make_physdesc(physdesc, record))
	else:
		physdescs.append(E.physdesc(E.extent("1 unknown")))

	return physdescs


def make_physdesc(physdesc, record):
	physdesc = E.physdesc(
		make_extent(physdesc),
		make_physfacet(physdesc),
		make_dimensions(physdesc, record)
		)

	return physdesc

def make_extent(physdesc):
	extents = physdesc.xpath("./marc:subfield[@code='a']", namespaces=ns)

	if extents:
		extent = extents[0]
		return E.extent(extent.text.strip().rstrip(".").rstrip(":").strip())
	else:
		return ""

def make_physfacet(physdesc):
	physfacets = physdesc.xpath("./marc:subfield[@code='b']", namespaces=ns) + physdesc.xpath("./marc:subfield[@code='e']", namespaces=ns) + physdesc.xpath("./marc:subfield[@code='3']", namespaces=ns)

	if physfacets:
		physfacet_note = ""
		for physfacet in physfacets:
			physfacet_note += "\n" + physfacet.text.strip().rstrip(";").strip()
		return E.physfacet(physfacet_note)
	else:
		return ""

def make_dimensions(physdesc, record):
	dimensions = physdesc.xpath("./marc:subfield[@code='c']", namespaces=ns)
	durations = record.xpath("./marc:datafield[@tag='306']/marc:subfield[@code='a']", namespaces=ns)

	if dimensions or durations:
		dimensions_texts = []
		dimensions_texts.extend([dimension.text.strip() for dimension in dimensions])
		dimensions_texts.extend([duration.text.strip() for duration in durations])
		dimensions_text = "; ".join(dimensions_texts)

		return E.dimensions(dimensions_text)
	else:
		return ""

def make_phystech(record):
	phystechs = record.xpath("./marc:datafield[@tago='538']/marc:subfield[@code='a']", namespaces=ns)

	if phystechs:
		phystech = phystechs[0].text.strip()

		return E.phystech(phystech)
	else:
		return ""

def make_descgrp(record):
	descgrp = E.descgrp(
		make_acqinfo(record),
		make_accruals(record),
		make_accessrestrict(record),
		make_userestrict(record),
		make_custodhist(record),
		make_phystech(record),
		make_altformavail(record),
		make_originalsloc(record),
		make_otherfindaid(record),
		make_relatedmaterial(record)
		)

	odds = make_odds(record)
	for odd in odds:
		descgrp.append(odd)

	return descgrp

def make_altformavail(record):
	altformavails = record.xpath("./marc:datafield[@tag='530']", namespaces=ns)

	if altformavails:
		altformavail = altformavails[0]
		altformavail_notes = altformavail.xpath("./marc:subfield[@code='a']", namespaces=ns) + altformavail.xpath("./marc:subfield[@code='3']", namespaces=ns)
		altformavail_texts = [altformavail.text.strip() for altformavail in altformavail_notes]
		altformavail_text = " ".join(altformavail_texts)

		return E.altformavail(altformavail_text)
	else:
		return ""

def make_originalsloc(record):
	originalslocs = record.xpath("./marc:datafield[@tag='534']", namespaces=ns) + record.xpath("./marc:datafield[@tag='535']", namespaces=ns)

	if originalslocs:
		originalsloc = originalslocs[0]
		originalsloc_note = ""
		for subfield in originalsloc.xpath("./marc:subfield", namespaces=ns):
			originalsloc_note += "\n{}".format(subfield.text.strip())

		return E.originalsloc(originalsloc_note.strip())
	else:
		return ""

def make_otherfindaid(record):
	otherfindaids = record.xpath("./marc:datafield[@tag='555']/marc:subfield[@code='a']", namespaces=ns)

	if otherfindaids:
		otherfindaid = otherfindaids[0].text.strip()
		return E.otherfindaid(otherfindaid)
	else:
		return ""

def make_relatedmaterial(record):
	relatedmaterials = record.xpath("./marc:datafield[@tag='544']", namespaces=ns)

	if relatedmaterials:
		relatedmaterial = relatedmaterials[0]
		relatedmaterial_note = ""
		for subfield in relatedmaterial.xpath("./marc:subfield", namespaces=ns):
			relatedmaterial_note += "\n{}".format(subfield.text.strip())

		return E.relatedmaterial(relatedmaterial_note.strip())
	else:
		return ""

def make_custodhist(record):
	custodhists = record.xpath("./marc:datafield[@tag='561']", namespaces=ns)

	if custodhists:
		custodhist = custodhists[0]
		custodhist_note = custodhist.xpath("./marc:subfield[@code='a']", namespaces=ns)[0].text.strip()
		materials_specified = custodhist.xpath("./marc:subfield[@code='3']", namespaces=ns)
		if materials_specified:
			custodhist_note += ": {}".format(materials_specified[0].text.strip())

		return E.custodhist(custodhist_note)
	else:
		return ""

def make_accessrestrict(record):
	accessrestricts = record.xpath("./marc:datafield[@tag='506']", namespaces=ns)

	if accessrestricts:
		accessrestrict = accessrestricts[0]
		accessrestrict_statement = accessrestrict.xpath("./marc:subfield[@code='a']", 
										namespaces=ns)[0].text.strip()
		if accessrestrict.xpath("./marc:subfield[@code='2']", namespaces=ns):
			accessrestrict_statement += " {}".format(accessrestrict.xpath("./marc:subfield[@code='2']", 
											namespaces=ns)[0].text.strip())
		return E.accessrestrict(accessrestrict_statement)
	else:
		return ""

def make_userestrict(record):
	userestrict = record.xpath("./marc:datafield[@tag='540']/marc:subfield[@code='a']", namespaces=ns)

	if userestrict:
		return E.userestrict(userestrict[0].text.strip())
	else:
		return ""

def make_acqinfo(record):
	acqinfo = record.xpath("./marc:datafield[@tag='541']/marc:subfield[@code='a']", namespaces=ns)

	if acqinfo:
		return E.acqinfo(acqinfo[0].text.strip())
	else:
		return ""

def make_accruals(record):
	accruals = record.xpath("./marc:datafield[@tag='584']/marc:subfield[@code='a']", namespaces=ns)

	if accruals:
		return E.accruals(accruals[0].text.strip())
	else:
		return ""

def make_bioghist(record):
	bioghists = record.xpath("./marc:datafield[@tag='545']", namespaces=ns)

	if bioghists:
		bioghist = bioghists[0]
		bioghist_statement = ""
		if bioghist.xpath("./marc:subfield[@code='a']", namespaces=ns):
			bioghist_statement += bioghist.xpath("./marc:subfield[@code='a']", 
									namespaces=ns)[0].text.strip()
		if bioghist.xpath("./marc:subfield[@code='b']", namespaces=ns):
			bioghist_statement += " " + bioghist.xpath("./marc:subfield[@code='b']", 
															namespaces=ns)[0].text.strip()

		return E.bioghist(bioghist_statement)
	else:
		return ""

def make_scopecontent(record):
	scopecontents = record.xpath("./marc:datafield[@tag='520']", namespaces=ns) + record.xpath("./marc:datafield[@tag='510']", namespaces=ns)

	if scopecontents:
		scopecontent = scopecontents[0]
		scopecontent_notes = scopecontent.xpath("./marc:subfield[@code='a']", namespaces=ns) + scopecontent.xpath("./marc:subfield[@code='b']", namespaces=ns)
		scopecontent_texts = [scopecontent.text.strip() for scopecontent in scopecontent_notes]
		scopecontent_text = " ".join(scopecontent_texts)

		return E.scopecontent(scopecontent_text)
	else:
		return ""

def make_arrangement(record):
	arrangements = record.xpath("./marc:datafield[@tag='351']", namespaces=ns)

	if arrangements:
		arrangement = arrangements[0]
		arrangement_notes = arrangement.xpath("./marc:subfield[@code='a']", namespaces=ns) + arrangement.xpath("./marc:subfield[@code='b']", namespaces=ns)
		arrangement_texts = [arrangement.text.strip() for arrangement in arrangement_notes]
		arrangement_text = " ".join(arrangement_texts)

		return E.arrangement(arrangement_text)
	else:
		return ""

def make_controlaccess(records):
	controlaccess = E.controlaccess()

	for record in records:
		subjects = make_subjects(record)
		persnames = make_persnames(record)
		famnames = make_famnames(record)
		corpnames = make_corpnames(record)

		for subject in subjects:
			controlaccess.append(subject)
		for persname in persnames:
			controlaccess.append(persname)
		for famname in famnames:
			controlaccess.append(famname)
		for corpname in corpnames:
			controlaccess.append(corpname)

	return controlaccess

def make_subjects(record):
	subjects_list = []

	tag_mappings = {
	"130":{
		"terms":{"a":"uniform_title", "h":"genre_form"}, 
		"indicator_sources":{},
		"alternate_sources":[]
		},
	"630":{
		"terms":{"a":"uniform_title", "v":"genre_form"}, 
		"indicator_sources":{"0":"lcsh"},
		"alternate_sources":[]
		},
	"650":{
		"terms":{"a":"topical", "b":"topical", "d":"temporal","v":"genre_form","x":"topical","y":"temporal","z":"geographic"}, 
		"indicator_sources":{"0":"lcsh", "2":"mesh", "4":"local"},
		"alternate_sources":["2"]
		},
	"651":{
		"terms":{"a":"geographic","v":"genre_form","x":"topical","y":"temporal","z":"geographic"},
		"indicator_sources":{"0":"lcsh","4":"local"}, 
		"alternate_sources":["2"]
		},
	"655":{
		"terms":{"a":"genre_form","v":"genre_form","y":"temporal","z":"geographic"},
		"indicator_sources":{"0":"lcsh", "4":"local"}, 
		"alternate_sources":["2"]
		},
	# The below is wrong... but it's what we have
	"656":{
		"terms":{"a":"genre_form"},
		"indicator_sources":{}, 
		"alternate_sources":["2"]
		},
	"690":{
		"terms":{"a":"topical","x":"topical","y":"temporal","z":"geographic"},
		"indicator_sources":{}, 
		"alternate_sources":[]
		},
	"691":{
		"terms":{"a":"geographic","x":"topical","y":"temporal"},
		"indicator_sources":{}, 
		"alternate_sources":[]
		},
	"730":{
		"terms":{"a":"uniform_title"}, 
		"indicator_sources":{},
		"alternate_sources":[]
		},
	"740":{
		"terms":{"a":"uniform_title","h":"genre_form"},
		"indicator_sources":{}, 
		"alternate_sources":[]
		},
	"830":{
		"terms":{"a":"uniform_title"}, 
		"indicator_sources":{},
		"alternate_sources":[]
		}
	}

	for tag in tag_mappings:
		subjects = record.xpath("./marc:datafield[@tag={}]".format(tag), namespaces=ns)
		term_types = tag_mappings[tag]["terms"]
		indicator_sources = tag_mappings[tag]["indicator_sources"]
		alternate_sources = tag_mappings[tag]["alternate_sources"]
		for subject in subjects:
			subjects_list.append(make_subject(subject, term_types, indicator_sources, alternate_sources))

	return subjects_list

def make_subject(subject, term_types, indicator_sources, alternate_sources):
	encodinganalog = subject.get("tag","")
	atts = {"encodinganalog":encodinganalog, "source":"local"}
	indicator_source_found = False
	if indicator_sources:
		indicator = subject.get("ind2", "")
		if indicator in indicator_sources:
			source = indicator_sources[indicator]
			atts["source"] = source.strip(".").strip("]")
			indicator_source_found = True
	if alternate_sources and not indicator_source_found:
		for code in alternate_sources:
			if subject.xpath("./marc:subfield[@code={}]".format(code), namespaces=ns):
				source = subject.xpath("./marc:subfield[@code={}]".format(code), namespaces=ns)[0].text.strip()
				atts["source"] = source.rstrip(".").strip("]")

	subject_element = E.subject(atts)

	for subfield in subject.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in term_types:
			term_type = term_types[code]
			term_text = subfield.text.strip()
			term = E.term({"type":term_type}, term_text)
			subject_element.append(term)

	return subject_element

def make_persnames(record):
	persnames_list = []
	persnames = record.xpath("./marc:datafield[@tag='600']", namespaces=ns) + record.xpath("./marc:datafield[@tag='700']", namespaces=ns)

	for persname in persnames:
		indicator1 = persname.get("ind1", "")
		if indicator1 != "3":
			persnames_list.append(make_persname(persname, "controlaccess"))

	return persnames_list

def make_persname(persname, context):
	encodinganalog = persname.get("tag","")

	if context == "origination":
		atts = {"encodinganalog":encodinganalog}
	elif context == "controlaccess":
		source_mappings = {"0": "lcnaf", "4":"local"}
		source_indicator = persname.get("ind2", "")
		if source_indicator in source_mappings:
			source = source_mappings[source_indicator]
		else:
			source = "local"

		atts = {"source":source, "encodinganalog":encodinganalog}

	relator_codes = ["4","e"]
	for subfield in persname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in relator_codes:
			atts["role"] = subfield.text.strip().rstrip(".")

	persname_element = E.persname(atts)

	primary_and_rest_of_name = persname.xpath("./marc:subfield[@code='a']", namespaces=ns)[0].text.strip().rstrip(",")
	name_parts = primary_and_rest_of_name.split(",")
	if len(name_parts) > 1:
		primary_name = name_parts[0].strip()
		rest_of_name = ",".join(name_parts[1:]).strip()
	else:
		primary_name = name_parts[0].strip()
		rest_of_name = ""
	persname_element.append(E.primary_name(primary_name))
	if rest_of_name:
		persname_element.append(E.rest_of_name(rest_of_name))

	persname_mappings = {"b":"number", "c":"title", "d": "dates", "q": "fuller_form"}
	for subfield in persname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in persname_mappings:
			tag = persname_mappings[code]
			element = etree.Element(tag)
			element.text = subfield.text.strip().rstrip(",").rstrip(".").strip()
			persname_element.append(element)

	term_mappings = {"t": "uniform_title", "v":"genre_form", "x": "topical", "y": "temporal", "z": "geographic"}
	for subfield in persname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in term_mappings:
			term_type = term_mappings[code]
			term = E.term({"type":term_type}, subfield.text.strip())
			persname_element.append(term)

	return persname_element

def make_corpnames(record):
	corpnames_list = []
	corpnames = record.xpath("./marc:datafield[@tag='610']", namespaces=ns) + record.xpath("./marc:datafield[@tag='611']", namespaces=ns) + record.xpath("./marc:datafield[@tag='710']", namespaces=ns)

	for corpname in corpnames:
		corpnames_list.append(make_corpname(corpname, "controlaccess"))

	return corpnames_list

def make_corpname(corpname, context):
	encodinganalog = corpname.get("tag","")
	if context == "origination":
		atts = {"encodinganalog":encodinganalog}
	elif context == "controlaccess":
		source_mappings = {"0": "lcnaf", "4":"local"}
		source_indicator = corpname.get("ind2", "")
		if source_indicator in source_mappings:
			source = source_mappings[source_indicator]
		elif corpname.xpath("./marc:subfield[@code='2']", namespaces=ns):
			source = corpname.xpath("./marc:subfield[@code='2']", namespaces=ns)[0].text.strip()
		else:
			source = "local"

		atts = {"source":source, "encodinganalog":encodinganalog}

	relator_codes = ["4","e"]
	for subfield in corpname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in relator_codes:
			atts["role"] = subfield.text.strip().rstrip(".").rstrip(",")

	corpname_element = E.corpname(atts)

	corpname_mappings = {"a":"primary_name","b":"subordinate_name", "n":"number"}
	for subfield in corpname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in corpname_mappings:
			tag = corpname_mappings[code]
			element = etree.Element(tag)
			element.text = subfield.text.strip().rstrip(".")
			corpname_element.append(element)

	term_mappings = {"t": "uniform_title", "v":"genre_form", "x": "topical", "y": "temporal", "z": "geographic"}
	for subfield in corpname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in term_mappings:
			term_type = term_mappings[code]
			term = E.term({"type":term_type}, subfield.text.strip())
			corpname_element.append(term)

	return corpname_element

def make_famnames(record):
	famnames_list = []
	famnames = record.xpath("./marc:datafield[@tag='600'][@ind1='3']", namespaces=ns)

	for famname in famnames:
		famnames_list.append(make_famname(famname, "controlaccess"))

	return famnames_list

def make_famname(famname, context):
	encodinganalog = famname.get("tag","")
	if context == "origination":
		atts = {"encodinganalog":encodinganalog}
	elif context == "controlaccess":
		source_mappings = {"0": "lcnaf", "4":"local"}
		source_indicator = famname.get("ind2", "")
		if source_indicator in source_mappings:
			source = source_mappings[source_indicator]
		else:
			source = "local"

		atts = {"source":source, "encodinganalog":encodinganalog}

	famname_element = E.famname(atts)

	famname_mappings = {"a":"family_name", "d":"dates", "c":"qualifier"}
	for subfield in famname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in famname_mappings:
			tag = famname_mappings[code]
			element = etree.Element(tag)
			element.text = subfield.text.strip().rstrip(".").rstrip(",")
			famname_element.append(element)

	term_mappings = {"t": "uniform_title", "v":"genre_form", "x": "topical", "y": "temporal", "z": "geographic"}
	for subfield in famname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in term_mappings:
			term_type = term_mappings[code]
			term = E.term({"type":term_type}, subfield.text.strip())
			famname_element.append(term)

	return famname_element

def make_odds(record):
	tag_mappings = {
	"240":"Uniform Title",
	"246":"Varying Form of Title",
	"250":"Edition Statement",
	"255":"Cartographic Mathematical Data",
	"260":"Publication, Distribution, Etc.",
	"440":"Series Statement",
	"490":"Series Statement",
	"500":"General Note",
	"502":"Dissertation Note",
	"504":"Bibliography",
	"505":"Formatted Contents Note",
	"508":"Creation/Production Credits",
	"511":"Participant or Performer",
	"518":"Date/Time and Place of Event",
	"521":"Target Audience",
	"533":"Reproduction Note",
	"550":"Issuing Body",
	"586":"Awards Note",
	"590":"General Note"
	}

	odds = []
	for tag in tag_mappings:
		odds.extend(record.xpath("./marc:datafield[@tag={}]".format(tag), namespaces=ns))

	odd_elements = []
	for odd in odds:
		odd_elements.append(make_odd(odd, tag_mappings))

	return odd_elements

def make_odd(odd, tag_mappings):
	tag = odd.get("tag", "")
	head_text = tag_mappings[tag]
	odd_element = E.odd(E.head(head_text))

	note_texts = []
	for subfield in odd.xpath("./marc:subfield", namespaces=ns):
		note_text = subfield.text.strip()
		note_texts.append(note_text)

	odd_text = " ".join(note_texts)
	odd_element.append(E.p(odd_text))

	return odd_element

def make_dsc(main_record, other_records):
	dsc = E.dsc(
		make_series(main_record),
		)

	for record in other_records:
		dsc.append(make_series(record))

	return dsc

def make_series(record):
	series = E.c01({"level":"series"},
		make_series_did(record),
		make_scopecontent(record)
		)

	#odds = make_odds(record)
	#for odd in odds:
		#series.append(odd)

	return series

def make_series_did(record):
	did = E.did(
		make_unittitle(record),
		make_accessrestrict(record),
		make_userestrict(record)
		)

	physdescs = make_physdescs(record)
	for physdesc in physdescs:
		did.append(physdesc)

	unitdates = make_unitdates(record, "series")
	for unitdate in unitdates:
		did.append(unitdate)

	return did

def make_ead_with_series(records):
	main_record, other_records = identify_main_record(records)
	if main_record and other_records:
		archdesc = make_archdesc(main_record)
		controlaccess = make_controlaccess(records)
		dsc = make_dsc(main_record, other_records)
		archdesc.append(controlaccess)
		archdesc.append(dsc)
		ead = E.ead(
			make_eadheader(main_record),
			archdesc
			)

		return ead

	else:
		return False

def make_ead_without_series(record):
	ead = E.ead(
		make_eadheader(record),
		make_archdesc(record)
		)

	return ead

def convert_marcxml_to_ead(marcxml_dir, ead_dir, unconverted_dir):
	for filename in os.listdir(marcxml_dir):
		print "Converting {} to EAD".format(filename)
		tree = etree.parse(join(marcxml_dir,filename))
		ns = {'marc': 'http://www.loc.gov/MARC21/slim'}
		records = tree.xpath('//marc:record', namespaces=ns)
		if len(records) > 1:
			# Make an EAD with series
			ead = make_ead_with_series(records)
		else:
			# Make only a collection level EAD
			record = records[0]
			ead = make_ead_without_series(record)

		if ead:
			with open(join(ead_dir, filename),'w') as f:
				f.write(etree.tostring(ead,encoding="utf-8",xml_declaration=True,pretty_print=True))
		else:
			shutil.copy(join(marcxml_dir, filename), unconverted_dir)

if __name__ == "__main__":
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	marcxml_dir = join(project_dir, "marcxml_no_ead_joined")
	ead_dir = join(project_dir, "converted_eads")
	unconverted_dir = join(project_dir, "unconverted_marcxml")
	convert_marcxml_to_ead(marcxml_dir, ead_dir, unconverted_dir)
