import asyncio
import requests
from pathlib import Path
import json

from pytonlib import TonlibClient
from tonsdk.utils import to_nano


    

async def get_block_transactions(client: TonlibClient, wc, shard, seqno):
    return (await client.get_block_transactions(workchain=wc, shard=shard, seqno=seqno, count=40))['transactions']


async def process_block(client, workchain, shard, seqno):
    transactions = await get_block_transactions(client, workchain, shard, seqno)
    for i,tr in enumerate(transactions):
            full_tr = (await client.get_transactions(account=tr['account'], from_transaction_lt=tr['lt'], from_transaction_hash=tr['hash']))[0]
            usdt_address = "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"  # Адрес контракта USDT
            if full_tr["out_msgs"] == []:
                continue
            elif usdt_address in full_tr["in_msg"]["destination"] or usdt_address in (full_tr["out_msgs"][0]["source"] or full_tr["out_msgs"][0]["destination"]):
                print(seqno,i,full_tr['transaction_id']['hash'])
            else:
                print(i,seqno)
            #print(i,full_tr['transaction_id']['hash'])
            #print(i,json.dumps(full_tr,indent=2))

    
async def main():


    # Загружаем конфигурацию сети TON
    url = 'https://ton.org/global.config.json'
    config = requests.get(url).json()

    # Создаем папку для хранения ключей
    keystore_dir = '/tmp/ton_keystore'
    Path(keystore_dir).mkdir(parents=True, exist_ok=True)

    # Создаем клиента TonlibClient
    client = TonlibClient(ls_index=2, config=config, keystore=keystore_dir, tonlib_timeout=10)
    await client.init()

    # Определяем начальный блок
    workchain = 0  # Workchain ID
    shard = 0  # Shard ID
    seqno = 43812580   # Block sequence number

    transactions = await get_block_transactions(client, 0, shard, seqno)
    while True:
        await process_block(client=client,workchain=workchain,shard=shard,seqno=seqno)
        seqno+=1


    

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())