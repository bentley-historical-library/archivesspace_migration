from os.path import join

from pre_aspace_cleanup.normalize_dates import normalize_dates
from pre_aspace_cleanup.authfilenumber_urls_to_uris import authfilenumber_urls_to_uris
from pre_aspace_cleanup.authfilenumber_propagation import authfilenumber_propagation
from pre_aspace_cleanup.fetch_dspace_mets import fetch_dspace_mets
from pre_aspace_cleanup.fix_collection_level_unittitle_commas import fix_collection_level_unittitle_commas
from pre_aspace_cleanup.note_to_odd import note_to_odd
from pre_aspace_cleanup.move_odds import move_odds
from pre_aspace_cleanup.move_daos import move_daos
from pre_aspace_cleanup.remove_and_between_dates import remove_and_between_dates
from pre_aspace_cleanup.remove_extent_parens import remove_extent_parens
from pre_aspace_cleanup.remove_expired_restrictions import remove_expired_restrictions
from pre_aspace_cleanup.remove_nested_genreforms import remove_nested_genreforms
from pre_aspace_cleanup.remove_unitdates_from_ps import remove_unitdates_from_ps
from pre_aspace_cleanup.wrap_unwrapped_unitdates import wrap_unwrapped_unitdates

from utilities.ead_cleanup.prettifydirectory import prettify_xml_in_directory

def run_pre_aspace_cleanup(ead_dir, dspace_mets_dir):
	fix_collection_level_unittitle_commas(ead_dir)
	wrap_unwrapped_unitdates(ead_dir)
	normalize_dates(ead_dir)
	authfilenumber_urls_to_uris(ead_dir)
	authfilenumber_propagation(ead_dir)
	fetch_dspace_mets(ead_dir, dspace_mets_dir)
	note_to_odd(ead_dir)
	move_odds(ead_dir)
	remove_unitdates_from_ps(ead_dir)
	move_daos(ead_dir)
	remove_and_between_dates(ead_dir)
	remove_extent_parens(ead_dir)
	remove_expired_restrictions(ead_dir)
	remove_nested_genreforms(ead_dir)
	prettify_xml_in_directory(ead_dir, ead_dir)
	print "*** RUN WALKER'S EXTENT NORMALIZATION SCRIPT ***"
	print "*** COPY THE MASTER FILES TO THE LOCAL EAD DIR"

def main():
	vandura_base_dir = 'C:/Users/djpillen/GitHub/vandura'
	vandura_real_masters_all = join(vandura_base_dir, 'Real_Masters_all')
	local_ead_dir = 'eads'
	dspace_mets_dir = 'C:/Users/djpillen/GitHub/dspace_mets'
	run_pre_aspace_cleanup(vandura_base_dir, dspace_mets_dir)
	run_pre_aspace_cleanup(vandura_real_masters_all, dspace_mets_dir)

if __name__ == "__main__":
	main()