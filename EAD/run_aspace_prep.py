from aspace_prep.camelcase_attributes import camelcase_attributes
from aspace_prep.add_classifications import add_classifications
from aspace_prep.amend_duplicate_call_numbers import amend_duplicate_call_numbers
from aspace_prep.add_container_parent_ids import add_container_parent_ids
from aspace_prep.add_container_barcodes import add_container_barcodes
from aspace_prep.get_compound_agents import get_compound_agents
from aspace_prep.get_subjects import get_subjects
from aspace_prep.skip_nested_items import skip_nested_items
from aspace_prep.subject_term_identification import subject_term_identification
from aspace_prep.add_compound_agent_terms import add_compound_agent_terms
from aspace_prep.remove_online_physlocs import remove_online_physlocs

from pre_aspace_cleanup.dspace_abstract_to_odd import dspace_abstract_to_odd


def run_aspace_prep(aspace_ead_dir, subjects_agents_dir, beal_classifications, dspace_mets_dir):
	camelcase_attributes(aspace_ead_dir)
	remove_online_physlocs(aspace_ead_dir)
	add_classifications(aspace_ead_dir, beal_classifications)
	amend_duplicate_call_numbers(aspace_ead_dir)
	skip_nested_items(aspace_ead_dir)
	dspace_abstract_to_odd(aspace_ead_dir, dspace_mets_dir)
	add_container_parent_ids(aspace_ead_dir)
	add_container_barcodes(aspace_ead_dir)
	get_compound_agents(aspace_ead_dir, subjects_agents_dir)
	get_subjects(aspace_ead_dir, subjects_agents_dir)
	subject_term_identification(aspace_ead_dir, subjects_agents_dir)

def main():
	aspace_ead_dir = 'eads'
	subjects_agents_dir = 'subjects_agents'
	beal_classifications = 'beal_classifications.csv'
	dspace_mets_dir = 'C:/Users/djpillen/GitHub/dspace_mets'
	run_aspace_prep(aspace_ead_dir, subjects_agents_dir, beal_classifications, dspace_mets_dir)

if __name__ == "__main__":
	main()