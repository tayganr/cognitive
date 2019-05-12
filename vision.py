import os
import json
import requests
import time
import csv
import config

DIR = config.image_dir
ENDPOINT = 'https://westeurope.api.cognitive.microsoft.com/vision/v2.0/recognizeText'
HTTP_HEADERS  = {
    'Ocp-Apim-Subscription-Key': config.api_key,
    'Content-Type': 'application/octet-stream'
}
HTTP_PARAMS   = {
    'mode': 'Handwritten',
}

# MAIN
def handler():
    table = []
    table_header = ('FILENAME', 'TEXT')
    table.append(table_header)
    for filename in sorted(os.listdir(DIR)):
        if filename.endswith("win (01).png"): 
            print('Processing: ' + filename)
            pathToImage = '{0}/{1}'.format(DIR, filename)
            response = process_img(pathToImage)
            data = get_data(response)
            parsed = parse_text(data)
            row = (filename, parsed)
            table.append(row)
    
    export('output', table)

# POST image for processing by Cognitive Services
def process_img(pathToImage):
    payload = open(pathToImage, 'rb').read()
    response = requests.post(ENDPOINT, headers=HTTP_HEADERS, params=HTTP_PARAMS, data=payload)
    return response

# Read JSON results from processed image
def get_data(response):
    time.sleep(1)
    poll = True
    results = None
    while (poll):
        response_final = requests.get(response.headers["Operation-Location"], headers=HTTP_HEADERS)
        results = response_final.json()
        if ('recognitionResult' in results) or ('status' in results and results['status'] == 'Failed'):
            poll = False
    return results

# Parse JSON results into text
def parse_text(results):
    text = ''
    for line in results['recognitionResult']['lines']:
        text += line['text'] + ' '
    return text  

# Export table array into CSV file
def export(filename, table):
    with open('{0}.csv'.format(filename), 'w',newline='', encoding="utf-8") as output:
        csv_writer = csv.writer(output)
        csv_writer.writerows(table)

if __name__ == '__main__':
    handler()
