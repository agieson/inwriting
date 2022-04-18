from web3 import Web3
from web3._utils.events import get_event_data
from eth_utils import event_abi_to_log_topic
from etherscan import Etherscan
import json


class Fetch:
    def __init__(self, provider, address, abi, blockNum, key, network):
        self.w3 = Web3(Web3.HTTPProvider(provider))
        self.contract_address = address
        self.block = blockNum
        with open(abi, 'r') as f:
            self.contract_abi = f.read()

        self.myContract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

        self.key = key
        self.eth = Etherscan(key, net=network)

        self.function_dict = {i['signature']: {'name': i['name'],
                                               'inputs': i['inputs'],
                                               'outputs': i['outputs']
                                               } for i in self.myContract.abi if i['type'] == 'function'}
        return

    def events(self, event="all", startBlock=None):
        if startBlock is None or startBlock == 0:
            startBlock = self.block
        if event.lower() == 'listed':
            return self.myContract.events.Listed.createFilter(fromBlock=f'{startBlock}').get_all_entries()
        elif event.lower() == 'bought':
            return self.myContract.events.Bought.createFilter(fromBlock=f'{startBlock}').get_all_entries()
        elif event.lower() == 'transfer':
            return self.myContract.events.Transfer.createFilter(fromBlock=f'{startBlock}').get_all_entries()
        elif event.lower() == 'approval':
            return self.myContract.events.Approval.createFilter(fromBlock=f'{startBlock}').get_all_entries()
        elif event.lower() == 'ownershiptransferred':
            return self.myContract.events.OwnershipTransferred.createFilter(fromBlock=f'{startBlock}').get_all_entries()
        elif event.lower() == 'mint':
            return [event for event in self.events('transfer') if int(event['args']['from'], 16) == 0]
        elif event.lower() == 'notmint':
            return [event for event in self.events('transfer') if int(event['args']['from'], 16) != 0]
        elif event.lower() == 'all':
            topic2abi = {event_abi_to_log_topic(_): _
                         for _ in self.myContract.abi if _['type'] == 'event'}

            logs = self.w3.eth.getLogs(dict(
                address=self.contract_address,
                fromBlock=startBlock,
                toBlock='latest'
            ))

            _return = []
            for entry in logs:
                topic0 = entry['topics'][0]
                if topic0 in topic2abi:
                    _return.append(get_event_data(self.w3.codec, topic2abi[topic0], entry))
            return _return
        else:
            raise AttributeError(
                'event field must be ["listed", "bought", "transfer", "approval", "ownershiptransferred", '
                '"mint", "notmint", "all"]')

    def transactions(self):
        return [txn['hash'] for txn in self.contract_txns(self.contract_address)]

    def contract_txns(self, address) -> dict:
        txns = self.eth.get_normal_txs_by_address(
            address=address,
            startblock=str(self.block),
            endblock='latest',
            sort='desc'
        )

        return txns

    def functions(self):
        txns = self.transactions()
        transfers = self.contractTransfers()
        txndict = dict()
        for txn in txns:
            data = self.w3.eth.get_transaction(txn)['input']
            for key in self.function_dict:
                if data.startswith(str(key)):
                    params = self.myContract.decode_function_input(data)
                    txndict.update({txn: {'function': params[0].fn_name,
                                          'inputs': params[1]}})
                    if params[0].fn_name.startswith('mint'):
                        for t in transfers:
                            if t['hash'] == txn:
                                txndict[txn].update({'tokenId': int(t['tokenID'])})
                                break
                    elif 'tokenId' in txndict[txn]['inputs'].keys():
                        txndict[txn].update({'tokenId': txndict[txn]['inputs']['tokenId']})

        return txndict

    def contractTransfers(self) -> dict:
        txns = self.eth.get_erc721_token_transfer_events_by_contract_address_paginated(
            contract_address=self.contract_address,
            page='1',
            offset='10000',
            sort='desc'
        )

        return txns


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    if (config['web3_provider_api_key'] or config['etherscan_api_key']) == '':
        raise AttributeError('config.json has not been properly filled out!')

    provider = config['web3_provider_api_key']
    contract_address = '0x4Ced71C6F18b112A36634eef5aCFA6156C6dADaD'  # In Writing contract address
    path_to_abi = 'abi.json'  # should be in the repo
    etherscan_key = config['etherscan_api_key']
    block = 14536393  # block where In Writing contract was deployed
    network = 'main'

    fetch = Fetch(provider, contract_address, path_to_abi, 14536393, etherscan_key, 'main')  # initialize fetch object

    out = fetch.functions()

    for i in out.keys():
        print(i, out[i])

