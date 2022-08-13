import csv
import os
import sys
import json
import requests
import pandas as pd

from dotenv import load_dotenv


# take environment variables from .env
load_dotenv()


def alchemy_api_url(address: str) -> str:
    """Gets API key and returns a string ready to send payload

      API key will be stored locally in the 'env' file; .env added to .gitignore for safety.
      Access the key variable and verify it is present, else notify user to add key to .env file 
      TODO: find a better way to handle adding missing key
      Two URLS needed:
      1. to get non-SPAM nfts only; NFTs that have been classified as spam. Spam classification has a wide range 
         of criteria that includes but is not limited to emitting fake events and copying other well-known NFTs.
      2. to get all nfts including SPAM; will filter the two dataframes to isolate spammy ones.
      3. to paginate the request as the results come with a `pageKey` if more pages exist.
      4. TODO: add url to getFloorPrice of the user NFT based of the contract addresses of the ones
         user holds

      Parameters
      ----------
      address:
      pagekey:

      Returns
      -------
      str: tuples consisting of URLs to query Alchemy API 
    """

    # check API key is assigned to variable
    try:
        api_key = os.getenv('ALCHEMY_API_KEY')
        print('API Key found!')
    except KeyError:
        print('API Key not set, please add your key to .env file.')

    print('validating address...')
    # check if address is valid
    valid = validate_address(address)

    # no spam
    nospam_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getNFTs?owner={valid}&withMetadata=true&filters[]=SPAM"

    # yes spam
    spam_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getNFTs?owner={valid}&withMetadata=true"

    # TODO: floor price by cotract api to floor prices for each of nfts owned; alpha right here!
    # floor_price_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getFloorPrice?contractAddress={contract}"

    return nospam_url, spam_url


def hexadecimal_address(address: str) -> bool:
    """Checks if address is hexadecimal

      Abstracting this function to handle hexadecimal check for validating 
      user's ethereum address.

      Parameters
      ----------
      address: potential hexadecimal address

      Returns
      -------
      bool: True if hexadecimal, otherwise False.
    """
    # check using python int() function
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def validate_address(address: str) -> str:
    """Validates address/ENS for NFT owner

      Requirements for a valid address:
      - 40-digit hexadecimal address
      - 42-digit hexadecimal address; prefix '0x' added
      - ENS: names must be 3 characters long, emojis are allowed, have to end with '.eth'

      If ENS name length is greater than or equal to 7 [name(3)+.(1)+eth (3)] and ends with '.eth', return address.
      If address is in a hexidecimal format then prefix it with '0x'. 
      If address is already of leght 42, return address. 
      If address is invalid, return None

      Parameters
      ----------
      address: potential ethereum address

      Returns
      -------
      address: an address/ENS with the correct format
    """

    # if ENS is >= 7 digit and ends with '.eth', return
    if address:
        # check if address is in hexadecimal format
        if hexadecimal_address(address):
            if len(address) == 42:
                return address

            if len(address) == 40:
                return '0x' + address

        else:
            print('Not a valid hexadecimal Eth address, (probably ENS)')

        # check ENS name validity
        print('Checking if ENS name...')
        if len(address) >= 7 and address.split('.')[1] == 'eth':
            return address
        else:
            print('Invalid ENS name! Try again.')
            sys.exit()


def pagination_api_url(address: str) -> str:
    """Returns pagination URLs to be passed into the requests parameters to query Alchemy API.

      API key will be stored locally in the 'env' file; .env added to .gitignore for safety.
      The address plus the Alchemy API is fed into the pagination URL and returned.
      TODO: find a better way to handle adding missing key
      Two URLS needed:
      1. pagination to get all non-SPAM nfts only; 
      2. pagination to get all SPAM nfts only;

      Parameters
      ----------
      address: owner address

      Returns
      -------
      str: tuples consisting of pagination URLs to query Alchemy API 
    """

    # API key has been checked previously
    api_key = os.getenv('ALCHEMY_API_KEY')

    # if valid, proceed and assign to URL
    if address:
        # non-spam pagination url
        paginate_nospam_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getNFTs?owner={address}&withMetadata=true&filters[]=SPAM"

        # spam pagination url
        paginate_spam_url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getNFTs?owner={address}&withMetadata=true"

        return paginate_nospam_url, paginate_spam_url

    else:
        print('Address not supplied! Try again.')
        sys.exit()


def get_nft_data(user_address) -> json:
    """Gets NFT data from Alchemy by address.

      Use the 4 URLs generated by the utility functions `alchemy_api_url` and `pagination_api_url`
      to pull non-spam and spam nft data including paginations.
      The address feeds into the function that collects data.
      The two utility functions supply URLs to pull data:
      - `alchemy_api_url` --> pulls unpaginated data; one page 
      - if first page has a `pageKey` value in response, use the modified `pagination_api_url` to get
        the rest of the data.

      Parameters
      ----------
      user_address: address/ENS of the owner

      Returns
      -------
      JSON: tuple JSON data not containing spam and those that do.
    """

    # generate initial urls
    nospam_url, spam_url = alchemy_api_url(user_address)

    # generate pagination urls
    paginate_nospam_url, paginate_spam_url = pagination_api_url(user_address)

    headers = {"Accept": "application/json"}

    # non-spam data container
    nospam_data = []

    # including spam data container
    spam_data = []

    def get_data(initial_url: str, pagination_url: str, sink: list) -> list:
        """Get data using Alchemy API.

        The first get data will use the non paginated form of the url to get data.
        If the response from inital request contains `pageKey` value, then insert the value
        into the pagination url and interate request until done.

        Parameters
        ----------
        intial_url: url for intial request
        pagination_url: url for pagination

        Returns
        -------
        JSON: tuple JSON data not containing spam and those that do.
        """

        # requesting data
        print("Downloading a batch of 100 nft data...")
        response = requests.get(url=initial_url, headers=headers)
        response.raise_for_status()
        result = response.json()

        # store the first result
        sink.append(result)

        # while result['pageKey'] is not empty, download the next 100 nft data
        # keep looping until no more pageKeys
        while "pageKey" in result:
            page = result['pageKey']
            paginate_nospam_url, paginate_spam_url = pagination_api_url(
                user_address)

            if page:
                print("Next page found, downloading the next batch(100) of nft data...")
                print()
                print('pageKey:', page)
                # print('url:', y_url)
                print()
                response = requests.get(
                    '{}&pageKey={}'.format(pagination_url, page), headers=headers)
                response.raise_for_status()
                result = response.json()
                sink.append(result)

            else:
                # if page is empty, break
                print('No more pages {}', page)
                print('----------------------')
                break

        return sink

    # get non-SPAM nfts for the given address
    not_spam = get_data(nospam_url, paginate_nospam_url, nospam_data)

    # get all nfts for the owner including SPAM
    is_spam = get_data(spam_url, paginate_spam_url, spam_data)

    return not_spam, is_spam


def normalize_data(results: list) -> pd.DataFrame:
    """Transform the downloaded NFT data to a final state, a dataframe.

      Takes in the JSON results then performs normalization using pandas.
      We are interested in the nft ownership data so we explode only the column 
      holding the data `df['ownedNfts']`.
      Perform one step of normalization for the exploded data before renaming the columns to 
      a better conventional name and convert the date column to datetime64[s].
      Return dataframe

      Parameters
      ----------
      results: json data from the get_data

      Returns
      -------
      pd.DataFrame: transformed dataframe
    """

    # make sure data is in container
    try:
        # normalize the downloaded JSON data
        normalize = pd.json_normalize(results)
    except KeyError as e:
        print(e)
        sys.exit()

    # I am only interested in data about NFTs owned by user
    df = normalize.explode("ownedNfts")

    # normalize the nested column
    df = pd.json_normalize(df['ownedNfts'])

    # pick out columns needed
    df = df[['timeLastUpdated', 'title', 'description',
             'contract.address', 'id.tokenMetadata.tokenType', 'tokenUri.raw']]

    # rename the columns
    df = df.rename(columns={'timeLastUpdated': 'last_updated', 'contract.address': 'contract_address',
                   'id.tokenMetadata.tokenType': 'token_type', 'tokenUri.raw': 'raw_token_uri'})

    # convert 'last_updated' column to datetime[s]
    df['last_updated'] = df['last_updated'].astype('datetime64[s]')

    return df


def df_to_csv(df: pd.DataFrame, title: str) -> csv:
    """Converts dataframe to a CSV file

      Parameters
      ----------
      df: dataframe from api request data
      title: name of CSV file

      Returns
      -------
      CSV file
      """
    return df.to_csv(title, index=False, encoding='utf-8')


def u_want_file(bag_df: pd.DataFrame) -> csv:
    """Takes a given pandas dataframe and converts it to CSV file before outputing it.

      Parameters
      ----------
      bag_df: dataframe to be converted to csv and downloaded

      Returns
      -------
      CSV: downloads a comma separated file with owner's nft data
    """

    title = ''
    while True:
        ask = input('Enter [Y/N] to proceed: ').lower()
        if ask == 'yes' or ask == 'y':
            title = input('What would you like to name the file? ').lower()
            title = title
            print('Converting your bag deets to CSV file...')
            df_to_csv(df=bag_df, title=title)
            name = title + '.csv'
            print('{} has been downloaded!'.format(name))
            break

        elif ask == 'no' or ask == 'n':
            print('You chose not to print.')
            break

        else:
            print('Invalid option. Try again.')
            continue

    return title
