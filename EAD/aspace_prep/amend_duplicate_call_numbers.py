from lxml import etree
import os
from os.path import join

def amend_duplicate_call_numbers(ead_dir):
    callnumbers = {}
    for filename in os.listdir(ead_dir):
        print 'Checking call numbers in {0}'.format(filename)
        tree = etree.parse(join(ead_dir, filename))
        callnumber = tree.xpath('//archdesc/did/unitid')[0].text.encode('utf-8').strip()
        if callnumber not in callnumbers:
            callnumbers[callnumber] = {}
            callnumbers[callnumber]['count'] = 0
            callnumbers[callnumber]['files'] = []
        callnumbers[callnumber]['count'] += 1
        callnumbers[callnumber]['files'].append(filename)

    for callnumber in callnumbers:
        if callnumbers[callnumber]['count'] > 1:
            for ead in callnumbers[callnumber]['files']:
                print "Amending call number {0} in {1}".format(callnumber, ead)
                tree = etree.parse(join(ead_dir,ead))
                eadid = tree.xpath('//eadid')[0].text.encode('utf-8').strip()
                collection_id = eadid.split('-')[-1]
                new_callnumber = "{0} [{1}]".format(callnumber, collection_id)
                old_callnumber = tree.xpath('//archdesc/did/unitid')[0]
                old_callnumber.text = new_callnumber
                with open(join(ead_dir,ead),'w') as ead_out:
                    ead_out.write(etree.tostring(tree,encoding='utf-8',pretty_print=True,xml_declaration=True))

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    amend_duplicate_call_numbers(aspace_ead_dir)

if __name__ == "__main__":
    main()