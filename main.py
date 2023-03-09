import os
import sys
import argparse
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv



def create_parser():
    parser = argparse.ArgumentParser(description='Сокращение ссылок с помощью API Bitly')
    parser.add_argument('name', help='Вставьте одну или несколько ссылок', nargs='+', default=[''])
    return parser


def shorten_link(url, BITLY_TOKEN):
    site = 'https://api-ssl.bitly.com/v4/bitlinks'
    header = {'Authorization': f'Bearer {BITLY_TOKEN}'}
    long_url = {'long_url': url}
    response = requests.post(site, headers=header, json=long_url)
    response.raise_for_status()
    items = response.json()
    return items['link']


def strip_scheme(url):
    parse_url = urlparse(url)
    bit_url = ''.join([parse_url.netloc, parse_url.path])
    return bit_url


def count_clicks(url, BITLY_TOKEN):
    bit_url = strip_scheme(url)
    site =f'https://api-ssl.bitly.com/v4/bitlinks/{bit_url}/clicks/summary'
    header = {'Authorization': f'Bearer {BITLY_TOKEN}'}
    params = {'unit': 'day', 'units': '-1'}
    response = requests.get(site, headers=header, params=params)
    response.raise_for_status()
    counts = response.json()
    return counts['total_clicks']


def is_bitlink(url, BITLY_TOKEN):
    bit_url = strip_scheme(url)
    site = f'https://api-ssl.bitly.com/v4/bitlinks/{bit_url}'
    header = {'Authorization': f'Bearer {BITLY_TOKEN}'}
    response = requests.get(site, headers=header)
    return response.ok


def main():
    BITLY_TOKEN = os.environ['BITLY_TOKEN']
    parser = create_parser()
    urls = parser.parse_args(sys.argv[1:])
    for url in urls.name:
        try:
            if is_bitlink(url, BITLY_TOKEN):
                count = count_clicks(url, BITLY_TOKEN)
                print('Количество переходов по ссылке bitly: ', count)
            else:
                bitlink = shorten_link(url, BITLY_TOKEN)
                print('Битлинк: ', bitlink)
        except requests.exceptions.HTTPError as exc:
            print(exc)


if __name__ == '__main__':
    load_dotenv()
    main()
