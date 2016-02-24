import os
from os.path import join
import shutil

def reconcile_muschbas(dst_dir):
	muschbas = ['muschba.xml', 'muschen.xml']
	for filename in os.listdir(dst_dir):
		if filename in muschbas:
			os.remove(join(dst_dir,filename))
			print "Removed {0}".format(filename)

def copy_eads(ead_dir, dst_dir):
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]

	for filename in filenames:
		print "Copying {0} to {1}".format(filename, dst_dir)
		src_file = join(ead_dir,filename)
		shutil.copy(src_file,dst_dir)

	reconcile_muschbas(dst_dir)

def main():
	vandura_base_dir = 'C:/Users/djpillen/GitHub/vandura'
	vandura_real_masters_all = join(vandura_base_dir, 'Real_Masters_all')
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	dst_dir = join(project_dir, 'eads')
	copy_eads(vandura_base_dir,dst_dir)
	copy_eads(vandura_real_masters_all, dst_dir)

if __name__ == "__main__":
	main()