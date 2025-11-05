# WhatsApp-QR
Toolkit demonstrating another approach of a QRLJacking attack, allowing to perform of remote account takeover, through sign-in QR code phishing.

This Python program clearly demonstrates how an attacker can hijack a victim's WhatsApp Web session by sending a phishing link (iPhone Win). Once the victim scans their QR code, the attacker gains full access to their WhatsApp Web account.

#Installation
Simply clone this repo on your local system by following the command
```bash
git clone https://github.com/kinghacker0/WhatsApp-QR
cd WhatsApp-QR
sudo apt install python3-pip python3-venv firefox-geckodriver
```
Install requirement packages
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
#Usage
```bash
python WhatsApp-QR.py
```
Now you can see the WhatsApp Web Window and Phishing URL on your terminal.
#License
WhatsApp-QR originally made by [zr0n](https://github.com/zr0n/whatsappsess)
