
readme_content = """
# Seed Phrase Encrypt/Decrypt Tool

This tool allows users to securely encrypt and decrypt Ethereum (EVM-compatible) seed phrases using password-based encryption. The application utilizes AES-256-CBC encryption, ensuring a safe method for handling sensitive seed phrases.

## Features
- **Encrypts** seed phrases with a user-defined password, generating an encrypted string.
- **Decrypts** encrypted seed strings using the same password to retrieve the original seed phrase.
- User-friendly graphical interface for easy interaction.

## Installation
To run this tool, you need to have Python 3.x installed along with the required libraries. Use the following command to install the necessary packages:

```bash
pip install pycryptodome tkinter
