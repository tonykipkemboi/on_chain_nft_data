from requests.models import HTTPError
from helpers import *


def main():
    """_summary_
    """

    print('##############################################')
    print('#           CHECK YOUR NFT BAG               #')
    print('##############################################')

    # owner enters address
    print()
    address = input('Please enter your ENS name or wallet address: ').lower()
    print('You entered: ', address)

    # get data after all checks complete on address
    print()
    print('Grabbing your data...')
    print()
    try:
        not_spam, is_spam = get_nft_data(address)
        print()
        print('Data grab complete!')
    except HTTPError as e:
        print()
        print('* Address might not have any NFTs. Confirm this manually on NFT marketplaces like OpenSea.')
        status_code = e.response.status_code
    print()
    print('Data grab complete!')

    print()
    print('Cleaning your non-spam nft data...')
    clean_bag = normalize_data(not_spam)

    print()
    print('Cleaning your spam nft data...')
    dirty_bag = normalize_data(is_spam)

    # filter and retain spam nfts
    dirty_tokens = pd.concat([clean_bag, dirty_bag]
                             ).drop_duplicates(keep=False)

    # count of NFTs; non-spammy ones
    clean_count = len(clean_bag)

    # count of NFTs; spammy ones
    dirty_count = len(dirty_tokens)

    # find token type percentage
    clean_token_percentage = clean_bag['token_type'].value_counts(
        normalize=True) * 100

    # find token type percentage
    dirty_token_percentage = dirty_tokens['token_type'].value_counts(
        normalize=True) * 100

    print()
    print('Cleanse complete!')

    print()
    print('##############################################')
    print('#        Quick stats on your NFT bag!        #')
    print('##############################################')

    print()
    print('Your Ethereum address is: ', address)
    print('🌄 You own {} non-SPAM NFT(s) 🔥'.format(clean_count))
    if dirty_count > 0:
        print('🌄 You own {} SPAM NFT(s) 😟'.format(dirty_count))
    else:
        if dirty_count == 0:
            print('🌄 You own {} SPAM NFT(s) 😎'.format(dirty_count))

    print('🌄 These are the percentage of unique non-SPAM token types you hold:\n{}'.format(
        clean_token_percentage.to_string()))
    print('🌄These are the percentage of unique SPAM token types you hold:\n{}'.format(
        dirty_token_percentage.to_string()))
    print('##############################################')

    print()
    print('Clean non-SPAM bag:')
    print(clean_bag)

    print()
    print('SPAM bag:')
    print()
    print(dirty_tokens)

    print()

    print()
    # if owner needs to download a CSV copy of the data; ask if clean or dirty
    # proceed to download the file
    clean = clean_bag
    dirty = dirty_tokens

    want_bag = input(
        'Would you like a CSV download of your data? [Y/N]').lower()

    if want_bag == 'yes' or want_bag == 'y':
        print('Downloading your clean bag...')
        clean_output = u_want_file(bag_df=clean)
        print('Downloading your dirty bag...')
        dirty_output = u_want_file(bag_df=dirty)

    else:
        print('See ya!')


if __name__ == "__main__":
    main()
