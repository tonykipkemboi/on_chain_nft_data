import requests
import json


def alchemy_api_url(api_key: str, address: str) -> str:
    nospam_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getNFTs?owner={address}&withMetadata=true&filters[]=SPAM"
    spam_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getNFTs?owner={address}&withMetadata=true"
    return nospam_url, spam_url


def pagination_api_url(api_key: str, address: str) -> str:
    paginate_nospam_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getNFTs?owner={address}&withMetadata=true&filters[]=SPAM"
    paginate_spam_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getNFTs?owner={address}&withMetadata=true"
    return paginate_nospam_url, paginate_spam_url


def floor_price_api(api_key: str, contract: str) -> str:
    contract_api_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getFloorPrice?contractAddress={contract}"
    return contract_api_url


def get_data(initial_url: str, pagination_url: str, api_key: str) -> list:
    headers = {"Accept": "application/json"}
    sink = []

    with requests.Session() as session:
        session.headers.update(headers)

        response = session.get(url=initial_url)
        if response.status_code != 200:
            print(
                f"Error: Failed to fetch data from {initial_url}. Status code: {response.status_code}")
            return sink

        result = response.json()
        sink.append(result)

        while "pageKey" in result:
            page = result['pageKey']
            if page:
                response = session.get(
                    '{}&pageKey={}'.format(pagination_url, page))
                if response.status_code != 200:
                    print(
                        f"Error: Failed to fetch data from {pagination_url}. Status code: {response.status_code}")
                    break
                result = response.json()
                sink.append(result)
            else:
                break

    return sink


def get_nft_data(api_key: str, user_address) -> json:
    nospam_url, spam_url = alchemy_api_url(api_key, user_address)
    paginate_nospam_url, paginate_spam_url = pagination_api_url(
        api_key, user_address)

    not_spam = get_data(nospam_url, paginate_nospam_url, api_key)
    is_spam = get_data(spam_url, paginate_spam_url, api_key)

    return not_spam, is_spam
