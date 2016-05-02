"""
Scraper for PCC data
"""
import csv
import sys

from lxml.html import fromstring
import requests

areas = [

    'Avon Somerset',
    'Bedfordshire',
    'Cambridgeshire',
    'Cheshire',
    'Cleveland',
    'Cumbria',
    'Derbyshire',
    'Devon Cornwall',
    'Dorset',
    'Durham',
    'Dyfed-Powys',
    'Essex',
    'Gloucestershire',
    'Gwent',
    'Hampshire',
    'Hertfordshire',
    'Humberside',
    'Kent',
    'Lancashire',
    'Leicestershire',
    'Lincolnshire',
    'Merseyside',
    'Norfolk',
    'North Wales',
    'North Yorkshire',
    'Northamptonshire',
    'Northumbria',
    'Nottinghamshire',
    'South Wales',
    'South Yorkshire',
    'Staffordshire',
    'Suffolk',
    'Surrey',
    'Sussex',
    'Thames Valley',
    'Warwickshire',
    'West Mercia',
    'West Midlands',
    'West Yorkshire',
    'Wiltshire'
    ]

BASE_AREA_URL = 'https://www.choosemypcc.org.uk/area/{0}'

def astree(url):
    """
    Helper that returns a URL as a lxml tree
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print resp.content
        msg = 'FTWError ({0})- File ({1})Not Found'.format(resp.status_code, url)
        raise Exception(msg)
    content = resp.text
    dom = fromstring(content)
    dom.make_links_absolute(url)
    return dom

def list_of_candidate_urls(area_url):
    """
    Given the AREA_URL for a PCC area, return a list of urls for the candidates
    """
    tree = astree(area_url)
    return [e.getparent().get('href') for e in tree.cssselect('.row.candidate')]

def candidate_dict_from_url(url):
    """
    Given a URL, return a dictionary with candidate data.
    """
    tree = astree(url)

    party_image = ''
    face_image = ''

    party_images = tree.cssselect('.row.party img')
    if len(party_images) > 0:
        party_image = party_images[0].get('src')

    sidebar_images = [e.get('src') for e in tree.cssselect('.sidebar img')]

    for i in sidebar_images:
        if i != party_image:
            face_image = i

    chat = u"\n".join([e.text_content() for e in tree.cssselect('.col-md-9 p,.col-md-9 ul')])
    chat = chat.encode('utf-8')

    return dict(
        name=tree.cssselect('.col-md-9 h1')[0].text_content().encode('utf-8'),
        face=face_image,
        party=tree.cssselect('.row.party')[0].text_content().replace('Force area', '').strip().encode('utf-8'),
        party_image=party_image,
        chat=chat,
        url=url
    )

def get_candidates(area):
    """
    Generator which, given the name of an AREA, will iterate through
    the candidates for it as dictionaries
    """
    area_url = BASE_AREA_URL.format(area.lower().replace(' ', '-'))
    candidate_urls = list_of_candidate_urls(area_url)
    for candidate_url in candidate_urls:
        yield candidate_dict_from_url(candidate_url)


def main():
    fieldnames = ['name', 'face', 'party', 'party_image', 'chat', 'url']
    with open('choosemypcc.people.csv', 'w') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for area in areas:
            print area
            for candidate in get_candidates(area):
                try:
                    writer.writerow(candidate)
                    print candidate['name']
                except:
                    print candidate
                    raise

    return 0

if __name__ == '__main__':
    sys.exit(main())
