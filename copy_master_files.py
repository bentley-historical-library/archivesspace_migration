from aspace_prep.copy_eads import copy_eads

vandura_base_dir = 'C:/Users/djpillen/GitHub/vandura'
vandura_real_masters_all = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
aspace_ead_dir = 'eads'

copy_eads(vandura_base_dir, aspace_ead_dir)
copy_eads(vandura_real_masters_all, aspace_ead_dir)