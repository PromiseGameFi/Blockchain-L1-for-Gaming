import pytest
from key_utils import private_key_to_wif, private_key_to_public_key, public_key_to_address
from ecdsa import SECP256k1

def test_private_key_to_wif():
    private_key = bytes.fromhex("your_test_private_key_here")  # Replace with actual private key
    wif = private_key_to_wif(private_key, compressed=True)
    expected_wif = "KwdMA...your_expected_wif_here..."  # Replace with expected WIF output
    assert wif == expected_wif

def test_private_key_to_public_key_compressed():
    private_key = bytes.fromhex("your_test_private_key_here")  # Replace with actual private key
    public_key = private_key_to_public_key(private_key, compressed=True)
    expected_public_key = bytes.fromhex("your_expected_compressed_public_key_here")  # Replace with expected output
    assert public_key == expected_public_key


def test_private_key_to_public_key_uncompressed():
    private_key = bytes.fromhex("your_test_private_key_here")  # Replace with actual private key
    public_key = private_key_to_public_key(private_key, compressed=False)
    expected_public_key = bytes.fromhex("your_expected_uncompressed_public_key_here")  # Replace with expected output
    assert public_key == expected_public_key

def test_public_key_to_address():
    public_key = bytes.fromhex("your_test_public_key_here")  # Replace with actual public key
    address = public_key_to_address(public_key)
    expected_address = "0x1234...your_expected_address_here..."  # Replace with expected Ethereum address
    assert address == expected_address
