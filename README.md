# BHL EAD ArchivesSpace Migration
EAD cleanup, prep, conversion, and posting scripts for the Bentley's ArchivesSpace migration.

##Requirements
* Walker's [bentley_code](https://github.com/walkerdb/bentley_code) repository (in particular, the agent mapping, extent normalization, and unitdates_in_unittitles normalization scripts) and associated requirements
* [lxml](http://lxml.de/)

##Running Order
1. run_pre_aspace_cleanup.py [this can be run at any time on the BHL's EADs]
2. Walker's [extent normalization](https://github.com/walkerdb/bentley_code/tree/master/normalization/aspaceify_extents)
3. copy_master_files.py
4. run_aspace_prep.py
5. archivesspace_defaults.py
6. Walker's [agent mapping](https://github.com/walkerdb/bentley_code/tree/master/mapping/aspace_agent_mapping)
7. run_aspace_preliminary_postings.py
8. Walker's [unitdate_unittitle_fix](https://github.com/walkerdb/bentley_code/tree/master/normalization/unitdates_in_unittitles)
9. capitalize_unittitles.py
10. run_aspace_verification.py
11. run_aspace_ead_migration.py
