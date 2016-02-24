import csv
import json
import requests
from os.path import join

def post_subjects(ead_dir, subjects_agents_dir, aspace_url, username, password):
    subjects_csv = join(subjects_agents_dir, 'aspace_subjects.csv')
    posted_csv = join(subjects_agents_dir, 'posted_subjects.csv')
    text_to_authfilenumber_csv = join(subjects_agents_dir, 'text_to_authfilenumber.csv')

    text_to_authfilenumber = {}
    with open(text_to_authfilenumber_csv,'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            sub_text = row[0]
            authfilenumber = row[1]
            text_to_authfilenumber[sub_text] = authfilenumber

    auth = requests.post(aspace_url + '/users/'+username+'/login?password='+password).json()
    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session}

    subjects_data = []
    with open(subjects_csv,'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            row_indexes = len(row) - 1
            source = row[1]
            full_text = row[2]
            if full_text in text_to_authfilenumber:
                authfilenumber = text_to_authfilenumber[full_text]
            else:
                authfilenumber = ''
            terms_list = []
            for row_num in range(3,row_indexes + 1, 2):
                term = row[row_num]
                term_type = row[row_num+1]
                terms_dict = {}
                terms_dict["term"] = term
                terms_dict["term_type"] = term_type
                terms_dict["vocabulary"] = "/vocabularies/1"
                terms_list.append(terms_dict)

            data = json.dumps({"authority_id":authfilenumber,"source":source,"vocabulary":"/vocabularies/1","terms":[i for i in terms_list]})
            subjects = requests.post(aspace_url+'/subjects', headers=headers, data=data).json()
            if 'status' in subjects:
                if subjects['status'] == 'Created':
                    print subjects
                    subject_uri = subjects['uri']
                    row.append(subject_uri)
                    subjects_data.append(row)

    with open(posted_csv,'ab') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerows(subjects_data)

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    subjects_agents_dir = join(project_dir,'subjects_agents')
    aspace_url = 'http://localhost:8089'
    username = 'admin'
    password = 'admin'
    post_subjects(aspace_ead_dir, subjects_agents_dir, aspace_url, username, password)

if __name__ == "__main__":
    main()
