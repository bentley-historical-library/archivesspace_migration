import getpass
from os.path import join

from aspace_prep.add_compound_agent_terms import add_compound_agent_terms

from aspace_migration.post_subjects import post_subjects
from aspace_migration.update_posted_subjects import update_posted_subjects
from aspace_migration.post_digital_objects import post_digital_objects
from aspace_migration.update_posted_digital_objects import update_posted_digital_objects
from aspace_migration.find_missing_refs import find_missing_refs

def run_aspace_preliminary_postings(aspace_ead_dir, subjects_agents_dir, digital_objects_dir, json_dir, resources_dir, migration_stats_dir, dspace_mets_dir, aspace_url, username, password):
	post_subjects(aspace_ead_dir, subjects_agents_dir, aspace_url, username, password)
	update_posted_subjects(aspace_ead_dir, subjects_agents_dir)
	post_digital_objects(aspace_ead_dir, digital_objects_dir, dspace_mets_dir, aspace_url, username, password,delete_csvs=True)
	update_posted_digital_objects(aspace_ead_dir, digital_objects_dir)
	add_compound_agent_terms(aspace_ead_dir, subjects_agents_dir)
	missing_refs = find_missing_refs(aspace_ead_dir)
	if missing_refs:
		for ref_type in missing_refs:
			print "Missing refs - {0}".format(ref_type)
			for filename in missing_refs[ref_type]:
				print filename

def main():
	aspace_ead_dir = 'eads'
	subjects_agents_dir = 'subjects_agents'
	digital_objects_dir = 'digital_objects'
	json_dir = 'json'
	resources_dir = 'resources'
	migration_stats_dir = 'migration_stats'
	dspace_mets_dir = 'C:/Users/djpillen/GitHub/dspace_mets'
	aspace_url = 'http://localhost:8089'
	username = 'admin'
	print "*** RUN THE FOLLOWING SCRIPTS ***"
	print "* archivesspace_defaults"
	print "* Walker's aspace_agent_mapping"
	print "****************************************"
	ready_to_go = raw_input("Have the scripts been run? (y/n): ")
	if ready_to_go.lower() == 'y':
		print "*** ArchivesSpace Information ***"
		print "URL: {0}".format(aspace_url)
		print "Username: {0}".format(username)
		print "*********************************"
		aspace_info_correct = raw_input("Is the above ASpace information correct? (y/n): ")
		if aspace_info_correct.lower() == 'y':
			password = getpass.getpass("Enter your ASpace password: ")
			run_aspace_preliminary_postings(aspace_ead_dir, subjects_agents_dir, digital_objects_dir, json_dir, resources_dir, migration_stats_dir, dspace_mets_dir, aspace_url, username, password)
			print "*** RUN WALKER'S UNITDATE_UNITTITLE_FIX SCRIPT ***"
			print "*** RUN THE RUN_UNITDATE_UNITTITLE_FIX_POST SCRIPT ***"
		else:
			print "Please fix the incorrect values and run the script again"
			quit()
	else:
		print "Please run the scripts and run this script again"
		quit()

if __name__ == "__main__":
	main()