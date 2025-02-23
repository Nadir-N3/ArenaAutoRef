import os
import secrets
import json
import random
import requests
import time
from datetime import datetime
from fake_useragent import UserAgent
from tqdm import tqdm
from eth_account import Account
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table

# Inisialisasi Rich Console
console = Console()

# Konfigurasi logging dengan RichHandler
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console)],
)
logger = logging.getLogger("ArenaVS-Bot")

# Header default untuk request
DEFAULT_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,id;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://quest.arenavs.com',
    'referer': 'https://quest.arenavs.com/',
}

# Daftar tugas
TASKS = {
    1: {"name": "Follow Twitter", "reward": 30000},
    2: {"name": "Like & Retweet", "reward": 14000},
    3: {"name": "Invite Friends", "reward": 30000},
    4: {"name": "Join Discord", "reward": 20000}
}

# Menampilkan banner dengan Rich Console
def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    console.print(f"""
[bold yellow]
╔══════════════════════════════════════════════╗
║     🏆 ARENA VS BOT - Automated Referrals   ║
║   Automate ArenaVS registrations & tasks!   ║
║  Developed by: https://t.me/sentineldiscus  ║
╚══════════════════════════════════════════════╝
[/bold yellow]
""")

# Membaca daftar proxy dari file
def load_proxies(filename='proxy.txt'):
    proxies = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    if "://" not in proxy:
                        proxy = f"http://{proxy}"
                    proxies.append(proxy)
    return proxies

# Mendapatkan proxy secara acak
def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

# Menyimpan proxy yang gagal ke proxyfailed.json
def save_failed_proxy(proxy, reason="Failed"):
    failed_data = []
    if os.path.exists('proxyfailed.json'):
        with open('proxyfailed.json', 'r') as f:
            failed_data = json.load(f)
    
    failed_data.append({"proxy": proxy, "reason": reason, "timestamp": datetime.now().isoformat()})
    with open('proxyfailed.json', 'w') as f:
        json.dump(failed_data, f, indent=4)

# Menghapus proxy yang gagal dari proxy.txt
def remove_failed_proxy(proxy, filename='proxy.txt'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        with open(filename, 'w') as f:
            for line in lines:
                cleaned_line = line.strip()
                cleaned_proxy = proxy.replace("http://", "").strip()
                if cleaned_line != cleaned_proxy:
                    f.write(line)

# Mengecek apakah proxy berfungsi
def check_proxy(proxy):
    url = "https://www.google.com"
    proxies = {'http': proxy, 'https': proxy}
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

# Membuat dompet Ethereum baru
def generate_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return private_key, acct.address

# Mendaftarkan dompet ke sistem ArenaVS dengan proxy
def register_wallet(wallet_address, referral_code, proxy):
    url = "https://quest-api.arenavs.com/api/v1/users/initialize"
    headers = {**DEFAULT_HEADERS, 'user-agent': UserAgent().chrome}
    data = {"walletAddress": wallet_address, "referralCode": referral_code}
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=15)
        if response.status_code == 429:  # Too Many Requests
            logger.debug(f"Rate limit hit (429) for wallet {wallet_address}. Retrying after delay...")
            time.sleep(5)  # Tambahkan delay lebih lama untuk 429
            response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=15)
            response.raise_for_status()
        else:
            response.raise_for_status()
        logger.debug(f"Registration response: {response.json()}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Registration failed for wallet {wallet_address}: {str(e)}")
        if proxy:
            save_failed_proxy(proxy, str(e))
            remove_failed_proxy(proxy)
        return None

# Fungsi untuk menyelesaikan tugas
def complete_task(user_id, task_id, token, proxy):
    url = f"https://quest-api.arenavs.com/api/v1/tasks/{task_id}/complete/{user_id}"
    headers = {**DEFAULT_HEADERS, 'user-agent': UserAgent().chrome, 'authorization': f'Bearer {token}'}
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        response = requests.post(url, headers=headers, json={}, proxies=proxies, timeout=15)
        if response.status_code == 429:
            logger.debug(f"Rate limit hit (429) for task {task_id}. Retrying after delay...")
            time.sleep(5)  # Delay untuk 429
            response = requests.post(url, headers=headers, json={}, proxies=proxies, timeout=15)
            response.raise_for_status()
        else:
            response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Task completion failed for task {task_id}: {str(e)}")
        if proxy:
            save_failed_proxy(proxy, str(e))
            remove_failed_proxy(proxy)
        return None

# Fungsi untuk mendapatkan data user
def get_user_data(wallet_address, token, proxy):
    url = f"https://quest-api.arenavs.com/api/v1/users/{wallet_address}"
    headers = {**DEFAULT_HEADERS, 'user-agent': UserAgent().chrome, 'authorization': f'Bearer {token}'}
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        if response.status_code == 429:
            logger.debug(f"Rate limit hit (429) for user data {wallet_address}. Retrying after delay...")
            time.sleep(5)
            response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            response.raise_for_status()
        else:
            response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch user data for wallet {wallet_address}: {str(e)}")
        if proxy:
            save_failed_proxy(proxy, str(e))
            remove_failed_proxy(proxy)
        return None

# Fungsi utama untuk memproses satu akun dan mengembalikan data untuk tabel
def process_account(wallet_num, referral_code, proxies, account_results):
    proxy = get_random_proxy(proxies)
    if proxy:
        if not check_proxy(proxy):
            logger.warning(f"Proxy {proxy} is not working. Removing...")
            save_failed_proxy(proxy, "Proxy not working")
            remove_failed_proxy(proxy)
            proxy = get_random_proxy(proxies)
    
    private_key, wallet_address = generate_wallet()
    logger.info(f"Account {wallet_num}: Generating Wallet {wallet_address[:10]}...")

    # Delay untuk menghindari 429
    time.sleep(random.uniform(1, 3))

    reg_response = register_wallet(wallet_address, referral_code, proxy)

    if not reg_response or "user" not in reg_response:
        logger.warning(f"Account {wallet_num}: Registration failed.")
        account_results.append({
            "No": wallet_num,
            "Wallet Address": wallet_address[:10] + "...",
            "Registration Status": "Failed",
            "Reason": "Invalid or missing response data",
            "XP": "N/A",
            "Task Status": "N/A"
        })
        return

    # Sesuaikan dengan struktur respons seperti di bot.py
    user = reg_response.get('user', {})
    user_id = user.get('id')
    token = reg_response.get('token')  # Ambil token dari tingkat utama respons, bukan dari 'user'
    refcode = user.get('referralCode')

    if not all([user_id, token, refcode]):
        logger.warning(f"Account {wallet_num}: Missing required user data (ID, token, or referral code).")
        account_results.append({
            "No": wallet_num,
            "Wallet Address": wallet_address[:10] + "...",
            "Registration Status": "Failed",
            "Reason": "Missing user data",
            "XP": "N/A",
            "Task Status": "N/A"
        })
        return

    logger.info(f"Account {wallet_num}: Registered successfully. User ID: {user_id}")

    task_status = {}
    for task_id, task_info in tqdm(TASKS.items(), desc=f"Account {wallet_num} Tasks", leave=False):
        logger.info(f"Account {wallet_num}: Completing {task_info['name']} (Reward: {task_info['reward']} XP)")
        result = complete_task(user_id, task_id, token, proxy)
        time.sleep(random.uniform(1, 2))  # Delay antar tugas

        status = "Completed" if result and result.get('status') else "Failed"
        task_status[task_info['name']] = status
        if status == "Completed":
            logger.info(f"Account {wallet_num}: {task_info['name']} completed!")
        else:
            logger.warning(f"Account {wallet_num}: Failed to complete {task_info['name']}")

    user_data = get_user_data(wallet_address, token, proxy)

    if user_data:
        with open('accounts.txt', 'a') as f:
            f.write(f"User ID: {user_id}\n")
            f.write(f"Private Key: {private_key}\n")
            f.write(f"Address: {wallet_address}\n")
            f.write(f"Referral Code: {refcode}\n")
            f.write(f"XP: {user_data.get('xp', 0)}\n")
            f.write("=" * 60 + "\n\n")

        logger.info(f"Account {wallet_num} saved to accounts.txt")

        # Tambahkan data ke daftar hasil untuk tabel
        task_summary = ", ".join([f"{name}: {status}" for name, status in task_status.items()])
        account_results.append({
            "No": wallet_num,
            "Wallet Address": wallet_address[:10] + "...",
            "Registration Status": "Success",
            "Reason": "",
            "XP": user_data.get('xp', 0),
            "Task Status": task_summary
        })

# Fungsi utama untuk menjalankan akun secara sekuensial
def main():
    show_banner()

    proxies = load_proxies()
    if proxies:
        logger.info(f"{len(proxies)} proxies loaded. Running with proxies.")
    else:
        logger.warning("No proxies found. Running without proxies.")

    referral_code = console.input("[yellow]🎟 Enter your referral code: [/yellow]")
    num_refs = int(console.input("[yellow]🔢 Enter number of referrals: [/yellow]"))

    console.print("\n")

    # Inisialisasi daftar untuk menyimpan hasil akun
    account_results = []

    with tqdm(total=num_refs, desc="Processing Accounts", ncols=80) as pbar:
        for i in range(1, num_refs + 1):
            process_account(i, referral_code, proxies, account_results)
            pbar.update(1)

    # Buat dan tampilkan tabel untuk semua akun yang diproses
    if account_results:
        account_table = Table(title="Account Processing Summary")
        account_table.add_column("No", style="cyan")
        account_table.add_column("Wallet Address", style="cyan")
        account_table.add_column("Registration Status", style="green")
        account_table.add_column("Reason", style="yellow")
        account_table.add_column("XP", style="cyan")
        account_table.add_column("Task Status", style="green")

        for result in account_results:
            account_table.add_row(
                str(result["No"]),
                result["Wallet Address"],
                result["Registration Status"],
                result["Reason"],
                str(result["XP"]) if "XP" in result else "N/A",
                result["Task Status"] if "Task Status" in result else "N/A"
            )

        console.print(account_table)
    else:
        logger.warning("No accounts were processed.")

    logger.info(f"Process completed! {len(account_results)} accounts processed.")

if __name__ == "__main__":
    main()
