import pytest
from bip38_utils import decrypt_bip38, encrypt_bip38

def test_decrypt_bip38_success():
    # Test with known BIP38 key and password
    bip38_key = "6PRNw7...your_test_key_here..."
    password = "correct_password"
    decrypted_key = decrypt_bip38(bip38_key, password)
    expected_private_key = bytes.fromhex("your_expected_private_key_here")  # Replace with expected output
    assert decrypted_key == expected_private_key

def test_decrypt_bip38_wrong_password():
    # Test with incorrect password
    bip38_key = "6PRNw7...your_test_key_here..."
    wrong_password = "wrong_password"
    with pytest.raises(ValueError):
        decrypt_bip38(bip38_key, wrong_password)

def test_encrypt_bip38_success():
    # Test encryption of private key
    private_key = bytes.fromhex("your_test_private_key_here")  # Replace with actual private key
    password = "correct_password"
    encrypted_key = encrypt_bip38(private_key, password, compressed=True)  # Change compressed as needed
    expected_bip38_key = "6PRNw7...your_expected_encrypted_key_here..."  # Replace with expected output
    assert encrypted_key == expected_bip38_key

def test_encryption():
    private_key= bytes.fromhex("your_test_private_key_here")
    password 