from lxml import etree
import os
from os.path import join
import re

def normalize_dates(ead_dir):
    yyyy = re.compile(r'^\d{4}$') # Ex: 1920
    yyyys = re.compile(r'^\d{4}s$') # Ex: 1920s
    yyyy_yyyy = re.compile(r'^\d{4}\-\d{4}$') # Ex: 1920-1930
    yyyys_yyyy = re.compile(r'^\d{4}s\-\d{4}$') # Ex: 1920s-1930
    yyyy_yyyys = re.compile(r'^\d{4}\-\d{4}s$') # Ex: 1920-1930s
    yyyys_yyyys = re.compile(r'^\d{4}s\-\d{4}s$') # Ex: 1920s-1930s
    undated = re.compile(r'^[Uu]ndated$')

    filenames = [filename for filename in os.listdir(ead_dir) if filename.endswith('.xml')]
    for filename in filenames:
        print "Normalizing dates in {0}".format(filename)
        tree = etree.parse(join(ead_dir, filename))
        unitdates = tree.xpath('//unitdate')
        for unitdate in unitdates:
            if not 'normal' in unitdate.attrib and not undated.match(unitdate.text.strip()):
                if unitdate.text and len(unitdate.text) > 0:
                    unitdate_text = unitdate.text.strip().encode('utf-8')
                    if yyyy.match(unitdate_text) and len(unitdate_text) == 4: # We also verify that the length is what we would expect based on the regular expression for an added level of certainty that these really are the kinds of dates we're looking for
                        unitdate.attrib['normal'] = unitdate_text # Dates like "1920" don't need to be changed at all to make a normalized version
                    elif yyyys.match(unitdate_text) and len(unitdate_text) == 5:
                        unitdate.attrib['normal'] = unitdate_text.replace('s', '') + '/' + unitdate.text[:3] + '9' # Change dates like "1920s" to "1920/1929"
                        unitdate.attrib['certainty'] = "approximate" # Since this is a date range and not an exact date, add an "approximate" certainty attribute
                    elif yyyy_yyyy.match(unitdate_text) and len(unitdate_text) == 9:
                        unitdate.attrib['normal'] = unitdate_text.replace('-', '/') # Dates like "1920-1930" are easy: simply replae the '-' with a '/' to get "1920/1930"
                    elif yyyys_yyyy.match(unitdate_text) and len(unitdate_text) == 10:
                        unitdate.attrib['normal'] = unitdate_text.replace('-', '/').replace('s', '') # "1920s-1930" becomes "1920/1930" by dropping the 's' and changing the '-' to a '/'
                        unitdate.attrib['certainty'] = "approximate"
                    elif yyyy_yyyys.match(unitdate_text) and len(unitdate_text) == 10:
                        normalized = unitdate_text.replace('-', '/') # For dates like "1920-1930s", first replace the '-' with a '/' to get "1920/1930s"
                        normalized = normalized.replace(normalized[-2:], '9') # Now replace the last two characters with '9', yielding "1920/1939"
                        unitdate.attrib['normal'] = normalized
                        unitdate.attrib['certainty'] = "approximate"
                    elif yyyys_yyyys.match(unitdate_text) and len(unitdate_text) == 11:
                        normalized = unitdate_text.replace('-', '/').replace('s', '', 1) # For dates like "1920s-1930s', replace the '-' with a '/' and remove ONLY the first 's' to get "1920/1930s"
                        normalized = normalized.replace(normalized[-2:], '9') # Now replace the last to characters with '9', yielding "1920/1939"
                        unitdate.attrib['normal'] = normalized
                        unitdate.attrib['certainty'] = "approximate"

        with open(join(ead_dir,filename),'w') as f:
            f.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
    ead_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
    normalize_dates(ead_dir)

if __name__ == "__main__":
    main()