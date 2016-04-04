import requests
from lxml import etree
import os
from os.path import join
import json
import re
import csv
import urlparse
import urllib2
import uuid
import getpass
import time

def post_digital_objects(ead_dir, digital_objects_dir, dspace_mets_dir, aspace_url, username, password,delete_csvs=False):

    if not os.path.exists(digital_objects_dir):
        os.makedirs(digital_objects_dir)

    posted_objects = join(digital_objects_dir, 'posted_digital_objects.csv')
    error_file = join(digital_objects_dir, 'digital_object_errors.txt')
    skipped_items_file = join(digital_objects_dir, 'skipped_items.txt')

    if delete_csvs:
        for csvfile in [posted_objects, error_file, skipped_items_file]:
            if os.path.exists(csvfile):
                os.remove(csvfile)

    already_posted = []

    if os.path.exists(posted_objects):
        with open(posted_objects,'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                href = row[0]
                if href not in already_posted:
                    already_posted.append(href)

    auth = requests.post(aspace_url+'/users/'+username+'/login?password='+password+'&expiring=false').json()
    session = auth['session']
    headers = {'X-ArchivesSpace-Session':session}

     # Iterate through EADs. If you find a dao href that is a DSpace handle, open the METS from the dspace_mets folder
     # Assemble the digital object and the components as such:
     # Digital object title == EAD component title and dates
     # Digital object identifer and file version uri == dao href
     # Digital object component titles = Titles from METS
     # Digital object component labels == Labels from METS
     # First, post the digital object
     # Then, grab the uri from the posted digital object to set as the parent for each component and post those

    posted_dig_objs = {}
    skipped_items = []

    for filename in os.listdir(ead_dir):
        print "Posting digital objects from {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        daos = tree.xpath('//dao')
        for dao in daos:
            did = dao.getparent()
            href = dao.attrib['href'].strip()
            # TO DO -- Account for the same href showing up in different places
            if 'show' in dao.attrib:
                show = dao.attrib['show']
            else:
                show = 'new'
            if 'actuate' in dao.attrib:
                actuate = dao.attrib['actuate']
            else:
                actuate = 'onRequest'
            xlink_actuate = actuate.replace('request','Request').replace('load','Load')
            if href.startswith('http://hdl.handle.net/2027.42') and href not in already_posted:
                handlepath = urlparse.urlparse(href).path
                the_id = handlepath.split('/')[-1]
                if the_id + '.xml' in os.listdir(dspace_mets_dir):
                    print "Parsing DSpace METS for", href
                    metstree = etree.parse(join(dspace_mets_dir, the_id + '.xml'))
                    ns = {'mets':'http://www.loc.gov/METS/','dim': 'http://www.dspace.org/xmlns/dspace/dim','xlink':'http://www.w3.org/TR/xlink/'}
                    XLINK = 'http://www.w3.org/TR/xlink/'

                    daodesc = dao.xpath('./daodesc/p')
                    if daodesc:
                        digital_object_note = re.sub(r'^\[|\]$','',daodesc[0].text)
                    else:
                        digital_object_note = False
                    if did.xpath('./unittitle'):
                        component_title = etree.tostring(did.xpath('./unittitle')[0])
                    else:
                        component_title = 'OOPS THERES NO TITLE HERE'
                    digital_object_title = re.sub(r'<(.*?)>','',component_title)

                    digital_object = {}
                    digital_object_components = []
                    digital_object['title'] = digital_object_title.strip()
                    digital_object['digital_object_id'] = str(uuid.uuid4())
                    digital_object['publish'] = True
                    digital_object['file_versions'] = [{'file_uri':href,'xlink_show_attribute':show,'xlink_actuate_attribute':xlink_actuate}]
                    if digital_object_note:
                        digital_object['notes'] = [{'type':'note','publish':True,'content':[digital_object_note],'jsonmodel_type':'note_digital_object'}]
                    digital_object_post = requests.post(aspace_url+'/repositories/2/digital_objects',headers=headers,data=json.dumps(digital_object)).json()

                    print digital_object_post

                    if 'error' in digital_object_post:
                        with open(error_file,'a') as f:
                            f.write(digital_object_post)

                    digital_object_uri = digital_object_post['uri']

                    with open(posted_objects,'ab') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([href,digital_object_uri])

                    posted_dig_objs[href] = digital_object_uri

                    fileGrp = metstree.xpath("//mets:fileGrp[@USE='CONTENT']",namespaces=ns)[0]
                    bitstreams = fileGrp.xpath('.//mets:file',namespaces=ns)
                    position = 0
                    for bitstream in bitstreams:
                        FLocat = bitstream.xpath('./mets:FLocat',namespaces=ns)[0]
                        # This was originally being added to each file_version as file_size_bytes, but the max integer allowed is 2,147,483,647
                        # Still storing this for now in case we want to turn it into something else (like an extent) later
                        component_size = bitstream.attrib['SIZE']
                        if '{%s}label' % (XLINK) in FLocat.attrib:
                            component_label = FLocat.attrib['{%s}label' % (XLINK)].strip()[:255]
                        else:
                            component_label = None
                        component_href = 'http://deepblue.lib.umich.edu' + FLocat.attrib['{%s}href' % (XLINK)] 
                        component_title = FLocat.attrib['{%s}title' % (XLINK)].strip()
                        digital_object_component = {
                            'digital_object':{'ref':digital_object_uri},
                            'title':component_title,
                            'label':component_label,
                            'position':position,
                            'file_versions':[{'file_uri':component_href}],
                            }
                        digital_object_components.append(digital_object_component)
                        position += 1

                    for component in digital_object_components:
                        digital_object_component_post = requests.post(aspace_url+'/repositories/2/digital_object_components',headers=headers,data=json.dumps(component)).json()
                        print digital_object_component_post

                        if 'error' in digital_object_component_post:
                            with open(error_file,'a') as f:
                                f.write(digital_object_component_post)
                else:
                    skipped_items.append(href)
                    with open(skipped_items_file,'a') as f:
                        f.write(href+'\n')

            elif href not in already_posted:

                daodesc = dao.xpath('./daodesc/p')
                if daodesc:
                    digital_object_note = re.sub(r'^\[|\]$','',daodesc[0].text)
                else:
                    digital_object_note = False

                component_title = etree.tostring(did.xpath('./unittitle')[0])
                digital_object_title = re.sub(r'<(.*?)>','',component_title)

                digital_object = {}
                digital_object['title'] = digital_object_title.strip()
                digital_object['digital_object_id'] = str(uuid.uuid4())
                digital_object['publish'] = True
                digital_object['file_versions'] = [{'file_uri':href,'xlink_show_attribute':show,'xlink_actuate_attribute':xlink_actuate}]
                if digital_object_note:
                    digital_object['notes'] = [{'type':'note','publish':True,'content':[digital_object_note],'jsonmodel_type':'note_digital_object'}]
                digital_object_post = requests.post(aspace_url+'/repositories/2/digital_objects',headers=headers,data=json.dumps(digital_object)).json()

                print digital_object_post

                if 'invalid_object' in digital_object_post:
                    with open(error_file,'a') as f:
                        f.write(digital_object_post)

                digital_object_uri = digital_object_post['uri']

                posted_dig_objs[href] = digital_object_uri

                with open(posted_objects,'ab') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([href,digital_object_uri])

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    digital_objects_dir = join(project_dir,'digital_objects')
    dspace_mets_dir = 'C:/Users/djpillen/GitHub/dspace_mets'
    aspace_url = 'http://localhost:8089'
    username = 'admin'
    password = 'admin'
    post_digital_objects(aspace_ead_dir, digital_objects_dir, dspace_mets_dir, aspace_url, username, password)