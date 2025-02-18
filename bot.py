import os
import secrets
import json
import random
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from fake_useragent import UserAgent
from tqdm import tqdm
from eth_account import Account
from colorama import Fore, Style, init

# Inisialisasi Colorama
init(autoreset=True)

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

# Menampilkan banner
def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"""{Fore.YELLOW}{Style.BRIGHT}
╔══════════════════════════════════════════════╗
║     🏆 ARENA VS BOT - Automated Referrals   ║
║   Automate ArenaVS registrations & tasks!   ║
║  Developed by: https://t.me/sentineldiscus  ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
""")

# Membaca daftar proxy dari file & mendeteksi jenisnya
def load_proxies(filename='proxy.txt'):
    proxies = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    if "://" not in proxy:  # Jika hanya IP:Port, default ke HTTP
                        proxy = f"http://{proxy}"
                    proxies.append(proxy)
    return proxies

# Mendapatkan proxy secara acak
def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

# Membuat dompet Ethereum baru
def generate_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return private_key, acct.address

# Mendaftarkan dompet ke sistem ArenaVS
def register_wallet(wallet_address, referral_code, proxy):
    url = "https://quest-api.arenavs.com/api/v1/users/initialize"
    headers = {**DEFAULT_HEADERS, 'user-agent': UserAgent().chrome}
    data = {"walletAddress": wallet_address, "referralCode": referral_code}
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=15)
        return response.json()
    except Exception:
        return None

# Menyelesaikan tugas
def complete_task(user_id, task_id, token, proxy):
    url = f"https://quest-api.arenavs.com/api/v1/tasks/{task_id}/complete/{user_id}"
    headers = {**DEFAULT_HEADERS, 'user-agent': UserAgent().chrome, 'authorization': f'Bearer {token}'}
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        response = requests.post(url, headers=headers, json={}, proxies=proxies, timeout=15)
        return response.json()
    except Exception:
        return None

# Mendapatkan data user
def get_user_data(wallet_address, token, proxy):
    url = f"https://quest-api.arenavs.com/api/v1/users/{wallet_address}"
    headers = {**DEFAULT_HEADERS, 'user-agent': UserAgent().chrome, 'authorization': f'Bearer {token}'}
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        return response.json()
    except Exception:
        return None

# Fungsi utama untuk memproses satu akun
def process_account(wallet_num, referral_code, proxies):
    proxy = get_random_proxy(proxies)
    private_key, wallet_address = generate_wallet()

    print(f"{Fore.CYAN}🔹 [{wallet_num}] Generating Wallet: {wallet_address}{Style.RESET_ALL}")
    if proxy:
        print(f"{Fore.YELLOW}🌐 [{wallet_num}] Using Proxy: {proxy}{Style.RESET_ALL}")

    reg_response = register_wallet(wallet_address, referral_code, proxy)

    if not reg_response or "user" not in reg_response or "token" not in reg_response:
        print(f"{Fore.RED}❌ [{wallet_num}] Registration failed! Skipping...{Style.RESET_ALL}")
        return

    user_id = reg_response['user']['id']
    token = reg_response['token']
    refcode = reg_response['user']['referralCode']

    print(f"{Fore.GREEN}✅ [{wallet_num}] Registration successful! User ID: {user_id}{Style.RESET_ALL}")

    for task_id, task_info in TASKS.items():
        print(f"{Fore.YELLOW}➡️ [{wallet_num}] Completing Task: {task_info['name']} (Reward: {task_info['reward']} XP){Style.RESET_ALL}")
        result = complete_task(user_id, task_id, token, proxy)

        if result and result.get('status'):
            print(f"{Fore.GREEN}✅ [{wallet_num}] {task_info['name']} completed!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ [{wallet_num}] Failed to complete {task_info['name']}{Style.RESET_ALL}")

    user_data = get_user_data(wallet_address, token, proxy)

    if user_data:
        with open('accounts.txt', 'a') as f:
            f.write(f"User ID: {user_id}\n")
            f.write(f"Private Key: {private_key}\n")
            f.write(f"Address: {wallet_address}\n")
            f.write(f"Referral Code: {refcode}\n")
            f.write(f"XP: {user_data.get('xp', 0)}\n")
            f.write("=" * 60 + "\n\n")

        print(f"{Fore.MAGENTA}💾 [{wallet_num}] Account saved to accounts.txt{Style.RESET_ALL}")

# Fungsi utama untuk menjalankan banyak akun sekaligus
def main():
    show_banner()
    
    proxies = load_proxies()
    if proxies:
        print(f"{Fore.GREEN}🔌 {len(proxies)} proxies loaded. Running with proxies.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️ No proxies found. Running without proxies.{Style.RESET_ALL}")

    referral_code = input(f"{Fore.YELLOW}🎟 Enter your referral code: {Style.RESET_ALL}")
    num_refs = int(input(f"{Fore.YELLOW}🔢 Enter number of referrals: {Style.RESET_ALL}"))

    try:
        max_threads = int(input(f"{Fore.YELLOW}⚡ Enter number of threads (default 5): {Style.RESET_ALL}").strip() or "5")
        if max_threads < 1:
            raise ValueError
    except ValueError:
        print(f"{Fore.RED}❌ Invalid input! Using default: 5 threads.{Style.RESET_ALL}")
        max_threads = 5

    print("\n")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        with tqdm(total=num_refs, desc="Processing", ncols=80) as pbar:
            futures = []
            for i in range(1, num_refs + 1):
                future = executor.submit(process_account, i, referral_code, proxies)
                future.add_done_callback(lambda _: pbar.update(1))
                futures.append(future)

            for future in futures:
                future.result()

    print(f"{Fore.GREEN}🎉 Process completed! {num_refs} wallets registered.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
    
