from lxml import etree
import os
from os.path import join
import uuid

def add_container_parent_ids(ead_dir):
    for filename in os.listdir(ead_dir):
        print "Adding container parent ids in {0}".format(filename)
        ead = etree.parse(join(ead_dir,filename))
        components = ead.xpath("//*[starts-with(local-name(), 'c0')]")
        rewrite = False
        for component in components:
            containers = component.xpath('./did/container')
            if len(containers) == 2:
                rewrite = True
                parent = containers[0]
                child = containers[1]
                parent_id = str(uuid.uuid4())
                parent.attrib['id'] = parent_id
                child.attrib['parent'] = parent_id
        if rewrite:
            with open(join(ead_dir, filename), 'w') as new_ead:
                new_ead.write(etree.tostring(ead, encoding="utf-8", xml_declaration=True,pretty_print=True))

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    add_container_parent_ids(aspace_ead_dir)

if __name__ == "__main__":
    main()