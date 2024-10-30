from typing import List

import json

from bip38 import BIP38
from bip38.cryptocurrencies import Bitcoin as Cryptocurrency
from bip38.wif import private_key_to_wif

# Private key
PRIVATE_KEY: str = "cbf4b9f70470856bb4f40f80b87edb90865997ffee6df315ab166d713af433a5"
# Passphrase / password
PASSPHRASE: str = "meherett"  # u"\u03D2\u0301\u0000\U00010400\U0001F4A9"
# Network type
NETWORK:str = "mainnet"
# To show detail
DETAIL: bool = True
# Initialize BIP38 instance
bip38: BIP38 = BIP38(
    cryptocurrency=Cryptocurrency, network=NETWORK
)
# Wallet Important Format's
WIFs: List[str] = [
    private_key_to_wif(
        private_key=PRIVATE_KEY, cryptocurrency=Cryptocurrency, network=NETWORK, wif_type="wif"
    ),  # No compression
    private_key_to_wif(
        private_key=PRIVATE_KEY, cryptocurrency=Cryptocurrency, network=NETWORK, wif_type="wif-compressed"
    )  # Compression
]

for WIF in WIFs:

    print("WIF:", WIF)

    encrypted_wif: str = bip38.encrypt(
        wif=WIF, passphrase=PASSPHRASE
    )
    print("BIP38 Encrypted WIF:", encrypted_wif)

    print("BIP38 Decrypted:", json.dumps(bip38.decrypt(
        encrypted_wif=encrypted_wif, passphrase=PASSPHRASE, detail=DETAIL
    ), indent=4))

    print("-" * 125)