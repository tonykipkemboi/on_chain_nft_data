import pandas as pd
from src.api.alchemy import floor_price_api
import requests


def get_floor_price(api_key: str, df: pd.DataFrame) -> pd.DataFrame:
    pd.options.display.float_format = '{:.4f}'.format
    nft_contracts = df['contract_address']
    url = [floor_price_api(api_key, nft_address)
           for nft_address in nft_contracts]
    headers = {"Accept": "application/json"}
    output = [(requests.get(i, headers=headers).json()) for i in url]
    data = pd.json_normalize(output).fillna('Not Available')
    data = data.rename(columns={'openSea.floorPrice': 'opensea_floorprice', 'openSea.priceCurrency': 'opensea_currency',
                       'looksRare.floorPrice': 'looksrare_floorprice', 'looksRare.priceCurrency': 'looksrare_currency'})
    data = data[['opensea_floorprice', 'opensea_currency',
                 'looksrare_floorprice', 'looksrare_currency']].copy()
    return data


def normalize_data(results: list) -> pd.DataFrame:
    normalize = pd.json_normalize(results)
    df = normalize.explode("ownedNfts")
    df = pd.json_normalize(df['ownedNfts'])
    df = df[['timeLastUpdated', 'title', 'description',
             'contract.address', 'id.tokenMetadata.tokenType', 'tokenUri.raw']]
    df = df.rename(columns={'timeLastUpdated': 'last_updated', 'contract.address': 'contract_address',
                   'id.tokenMetadata.tokenType': 'token_type', 'tokenUri.raw': 'raw_token_uri'})
    df['last_updated'] = df['last_updated'].astype('datetime64[s]')
    return df


def get_image_url(raw_token_uri):
    response = requests.get(raw_token_uri)
    data = response.json()
    return data.get('image_url')
