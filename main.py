import streamlit as st
from src.api.alchemy import get_nft_data
from src.utils.data_processing import normalize_data, get_floor_price
from src.utils.data_processing import get_image_url
from src.config import get_api_key
import pandas as pd


def main():
    st.title('🖼️ NFT Bag Checker App 💰')

    with st.form(key='address_form'):
        address = st.text_input('Enter your ENS name or wallet address 👇🏾 ')
        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        api_key = get_api_key()

        not_spam, is_spam = get_nft_data(api_key, address)

        clean_bag = normalize_data(not_spam)
        dirty_bag = normalize_data(is_spam)
        dirty_tokens = pd.concat([clean_bag, dirty_bag]
                                 ).drop_duplicates(keep=False)
        floor_price = get_floor_price(api_key, clean_bag)
        clean_bag = pd.concat([clean_bag, floor_price], axis=1)

        clean_count = len(clean_bag)
        dirty_count = len(dirty_tokens)

        clean_bag.replace('Not Available', pd.NA, inplace=True)
        clean_bag["opensea_floorprice"] = pd.to_numeric(clean_bag["opensea_floorprice"], errors='coerce')

        col1, col2, col3 = st.columns(3)

        # Check if the entered address matches an ENS name in the clean_bag DataFrame
        matching_nft = clean_bag[clean_bag['title'].str.contains(address, na=False)]
        if not matching_nft.empty:
            raw_token_uri = matching_nft['raw_token_uri'].values[0]
            image_url = get_image_url(raw_token_uri)
            if image_url is not None:
                col1.image(image_url)


        clean_token_percentage = clean_bag['token_type'].value_counts()
        dirty_token_percentage = dirty_tokens['token_type'].value_counts()

        col2.metric('Legit NFTs', clean_count)
        col2.metric('Legit ERC', clean_token_percentage.to_string())

        if dirty_count > 0:
            col3.metric('Spam NFTs', dirty_count)
            col3.metric('Spam ERC', dirty_token_percentage.to_string())
        else:
            col3.metric('Spam NFTs', dirty_count)
            col3.metric('Spam ERC', '0')

        st.dataframe(clean_bag)
        st.dataframe(dirty_tokens)

        csv = clean_bag.to_csv(index=False).encode()
        st.download_button(
            label="Download clean bag as CSV",
            data=csv,
            file_name='clean_bag.csv',
            mime='text/csv',
        )

    else:
        st.warning('💡 enter an ENS name or address to begin!')


if __name__ == "__main__":
    main()
