import { toNano } from '@ton/core';
import { ABSContract } from '../wrappers/ABSContract';
import { NetworkProvider } from '@ton/blueprint';

export async function run(provider: NetworkProvider) {
    const aBSContract = provider.open(await ABSContract.fromInit(BigInt(Math.floor(Math.random() * 10000))));

    await aBSContract.send(
        provider.sender(),
        {
            value: toNano('0.05'),
        },
        {
            $$type: 'Deploy',
            queryId: 0n,
        }
    );

    await provider.waitForDeploy(aBSContract.address);

    console.log('ID', await aBSContract.getId());
}
