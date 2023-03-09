import os
import sys
import argparse
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv



def create_parser():
    parser = argparse.ArgumentParser(description='Сокращение ссылок с помощью API Bitly')
    parser.add_argument('user_urls', help='Вставьте одну или несколько ссылок', nargs='+', default=[''])
    return parser


def shorten_link(url, bitly_token):
    site = 'https://api-ssl.bitly.com/v4/bitlinks'
    header = {'Authorization': f'Bearer {bitly_token}'}
    long_url = {'long_url': url}
    response = requests.post(site, headers=header, json=long_url)
    response.raise_for_status()
    bitlink = response.json()
    return bitlink['link']


def create_biturl(url):
    parsed_url = urlparse(url)
    bit_url = ''.join([parsed_url.netloc, parsed_url.path])
    return bit_url


def count_clicks(url, bitly_token):
    bit_url = create_biturl(url)
    site =f'https://api-ssl.bitly.com/v4/bitlinks/{bit_url}/clicks/summary'
    header = {'Authorization': f'Bearer {bitly_token}'}
    params = {'unit': 'day', 'units': '-1'}
    response = requests.get(site, headers=header, params=params)
    response.raise_for_status()
    counts = response.json()
    return counts['total_clicks']


def is_bitlink(url, bitly_token):
    bit_url = create_biturl(url)
    site = f'https://api-ssl.bitly.com/v4/bitlinks/{bit_url}'
    header = {'Authorization': f'Bearer {bitly_token}'}
    response = requests.get(site, headers=header)
    return response.ok


def main():
    bitly_token = os.environ['BITLY_TOKEN']
    parser = create_parser()
    urls = parser.parse_args()
    for url in urls.user_urls:
        try:
            if is_bitlink(url, bitly_token):
                count = count_clicks(url, bitly_token)
                print('Количество переходов по ссылке bitly: ', count)
            else:
                bitlink = shorten_link(url, bitly_token)
                print('Битлинк: ', bitlink)
        except requests.exceptions.HTTPError as exc:
            print(exc)


if __name__ == '__main__':
    load_dotenv()
    main()
