# In Writing
Files from the In Writing NFT project, as well as files to help developers connect In Writing to projects of their own!

## Getting Started
Clone this repository using the terminal command ```git clone https://github.com/agieson/inwriting.git```.

Install required packages listed in ```requirements.txt```.

Fill out the ```config.json``` with your Etherscan API key and your Web3 provider API key.

Run the test code provided for you in the main function of ```web3FetchScripts.py```!

## web3FetchScripts.py
### the Fetch class
The Fetch object is instantiated to "fetch" different things from the In Writing contract. Make sure to put
```provider_api_key, address, path_to_abi, block_number, etherscan_api_key, and nework``` in the constructor.
Once that's been done, the Fetch object is ready to use!

### Fetch.events
Fetches a list of events that have been emitted by the contract. If left blank, ```event``` will be set to ```'all'```, 
and ```startBlock``` will be set to ```self.block```. 

#### Event fields are as follows:
- ```all``` - all events
- ```transfer``` - only events where a token was transferred
- ```mint``` - only transfer events where tokens were transferred from the 0x0 address
- ```notmint``` - only transfer events where tokens were transferred from any address that is not the 0x0 address
- ```listed``` - only events where a token was listed for sale on the decentralized marketplace
- ```bought``` - only events where a token was bought on the decentralized marketplace
- ```approval``` - only events where a token was approved to be used by another address
- ```ownershiptransferred``` - only events where the ownership of the contract was transferred to another address

