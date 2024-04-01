import re
import requests
import json

def get_uniprot(ids: list):
    accessions = ','.join(ids)
    endpoint = "https://rest.uniprot.org/uniprotkb/accessions"
    http_function = requests.get
    http_args = {'params': {'accessions': accessions}}
    return http_function(endpoint, **http_args)


def get_ensembl(accessions_list):
    json_ids = json.dumps({"ids": accessions_list})
    server = "https://rest.ensembl.org"
    ext = "/lookup/id"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    r = requests.post(server + ext, headers=headers, data=f'{json_ids}')
    if not r.ok:
        raise ValueError('Incorrect data entered.')

    decoded = r.json()
    return decoded

def parse_response_uniprot(resp = None):
    resp = resp.json()
    resp = resp["results"]
    output = {}
    for val in resp:
        acc = val['primaryAccession']
        species = val['organism']['scientificName']
        gene = val['genes']
        seq = val['sequence']
        output[acc] = {'organism':species, 'geneInfo':gene, 'sequenceInfo':seq, 'type':'protein'}

    return output

def parse_response_ensembl(decoded):
    output = {}
    for val in decoded:
        acc = decoded[val]['id']
        species = decoded[val]['species']
        gene = decoded[val]['description']
        type = decoded[val]["object_type"]
        logic_name = decoded[val]['logic_name']
        output[acc] = {'organism':species, 'logic_name':logic_name, 'geneInfo':gene, 'type':type}

    return output

def parse_ID(ID_list):
    ensembl_match = all(re.search(r'(ENS([a-zA-Z]{0,4})|(MGP\D*))(E|FM|G|GT|P|RF|T)\d{11}', 'r' + ID) for ID in ID_list)
    uniprot_match = all(re.search(r'[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}', 'r' + ID) for ID in ID_list)

    if ensembl_match:
        return parse_response_ensembl(get_ensembl(ID_list))
    elif uniprot_match:
        return parse_response_uniprot(get_uniprot(ID_list))
    else:
        return 'Check the ids\' format'


accessions_list = list(input('Enter the IDs separated by spaces:').split())
print(parse_ID(accessions_list))
