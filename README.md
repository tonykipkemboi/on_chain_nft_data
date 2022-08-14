# On-chain NFT Data
This code pulls on-chain NFT data for a given wallet address or ENS name. 

The raw json data is normalized using `pandas.json_normalize` function and 
some simple analysis ran on the data based on the following user questions:

- How many SPAM and non-SPAM NFTs do I own?
  
- What percentage of each token type (i.e. ERC721/ERC1155/UNKNOWN) do I own?
  
There's an option to download your data as well, if you like!

Here's an example of NFTs held by `vitalik.eth` as of `8/12/2022`

![NFTs held by vitalik.eth](./vitalik_nft_data_snapshot.png)

## Installation Steps
My system setup:
- windows machine; windows guy here! (you can easily look up the equivalent commands for the systems you're working with)
- python 3.10.2 version
  
Clone the repository:

```
git clone https://github.com/tonykipkemboi/on_chain_nft_data
```

Go into the directory.
```
cd on_chain_nft_data
```

You have the option of running this app on the command line or opening it up in your favorite IDE (Integrated Development Environment).
Whichever option you choose, make sure to follow configure the below correctly.

**This next step is CRUCIAL, make sure to follow the instructions carefully**

Navigate to the file named `.env_example` and:
```
- Rename ".env_example" file to ".env"

- Add your [Alchemy API Key](https://www.alchemy.com/) in in between the quotes; ALCHEMY_API_KEY ="YOUR_ALCHEMY_API_KEY_GOES_HERE"

- Save the file!
```

Setup a `virtual environment` by running the following commands in your `windows terminal`:


- This will create a on-chain-nft-data/venv folder.
```
python -m venv venv
```

- Activate venv with the following command (different variations depending on your OS(Operating System))
```
.\venv\Scripts\activate
```

- Add venv to your .gitignore file if not added already.


You can tell the environment is active by looking at your terminal prompt. 
It will look something of the sort. Note the `venv` part: 

```
(venv) computer:on_chain_data user$
```

Install the dependencies required to run the program by running this command:

``` 
pip install -r requirements.txt
```


## Running the program on the Command Line 

Change directory into `app` folder to run the program as such;

- Change directory to app
```
cd app
```

Run the program;

```
python runner.py
```

After you're through and ready to close the terminal, `deactivate` the virtual environment by typing he following command;

``` 
deactivate
```

## Running the program on Jupyter Notebook

Alternatively, if you would like to play with the app in `Jupyter Notebook`, navigate to the root of the directory and type the following commands in your terminal/command line;

- Running the following command will create a kernel that can be used to run jupyter notebook commands inside the virtual environment.
  
``` 
ipython kernel install --user --name=venv
```
- Open Jupyter Notebook.
- 
```
jupyter notebook
``` 

This assumes you have Jupyter Notebook configured in yor system, if not, consider downloading [Anaconda](https://www.anaconda.com/)

For the `jupyter notebook`, run the cell using `Ctrl + Enter` or using the run button on the UI.


## Improvements & Next Steps

More info in this file.

[TODO](./on_chain_data/TODO.md)

- The query for owners with a lot of NFTs is taking a couple of minutes to run, here's stats for running `vitalik.eth`
  ``` 
  Execution time: ~ 3 minutes 30 seconds
  Total NFTs (at time of query): 20937 
  ```
- The latency could be improved by implementing concurrency.
