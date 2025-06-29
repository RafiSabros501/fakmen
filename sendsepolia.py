from web3 import Web3
import os

# Ganti dengan URL node provider Sepolia (contoh dengan Infura)
INFURA_PROJECT_ID = "YOUR_INFURA_PROJECT_ID"  # <-- Ganti dengan project ID-mu
provider_url = f"https://sepolia.infura.io/v3/{INFURA_PROJECT_ID}"
w3 = Web3(Web3.HTTPProvider(provider_url))

if not w3.is_connected():
    print("Tidak terhubung ke jaringan Sepolia!")
    exit(1)

def read_lines(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Baca private keys dan alamat penerima
pvkeys = read_lines("pvkeys.txt")
recipients = read_lines("wallet.txt")

if len(pvkeys) == 0 or len(recipients) == 0:
    print("File pvkeys.txt atau wallet.txt kosong!")
    exit(1)

print(f"Terdapat {len(pvkeys)} sender dan {len(recipients)} penerima.")

try:
    eth_amount = float(input("Berapa jumlah ETH (Sepolia) yang ingin dikirim per transaksi? "))
except ValueError:
    print("Input tidak valid.")
    exit(1)

value = w3.to_wei(eth_amount, 'ether')
chain_id = 11155111  # Chain ID Sepolia

def send_transaction(sender_pk, recipient, value, nonce):
    account = w3.eth.account.from_key(sender_pk)
    sender_address = account.address
    gas_price = w3.eth.gas_price

    tx = {
        'nonce': nonce,
        'to': recipient,
        'value': value,
        'gas': 21000,
        'gasPrice': gas_price,
        'chainId': chain_id
    }

    signed_tx = w3.eth.account.sign_transaction(tx, sender_pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

print("\nMulai mengirim transaksi...\n")

# Jika hanya ada 1 sender, gunakan sender tersebut untuk semua penerima
if len(pvkeys) == 1:
    sender_pk = pvkeys[0]
    account = w3.eth.account.from_key(sender_pk)
    sender_address = account.address
    # Dapatkan nonce awal dari jaringan
    current_nonce = w3.eth.get_transaction_count(sender_address)
    for idx, recipient in enumerate(recipients, start=1):
        try:
            tx_hash = send_transaction(sender_pk, recipient, value, current_nonce)
            print(f"[{idx}] Transaksi berhasil dikirim ke {recipient}! Tx hash: {tx_hash} (nonce: {current_nonce})")
            current_nonce += 1  # Increment nonce untuk transaksi berikutnya
        except Exception as e:
            print(f"[{idx}] Gagal mengirim transaksi ke {recipient}: {e}")
else:
    # Jika lebih dari 1 sender, pairing secara langsung menggunakan zip
    for idx, (sender_pk, recipient) in enumerate(zip(pvkeys, recipients), start=1):
        try:
            nonce = w3.eth.get_transaction_count(w3.eth.account.from_key(sender_pk).address)
            tx_hash = send_transaction(sender_pk, recipient, value, nonce)
            print(f"[{idx}] Transaksi berhasil dikirim! Tx hash: {tx_hash}")
        except Exception as e:
            print(f"[{idx}] Gagal mengirim transaksi: {e}")

print("\nSelesai mengirim transaksi.")
