from eth_account import Account
import secrets
import requests
import json
from fake_useragent import UserAgent
from colorama import Fore, Style, init
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Inisialisasi colorama
init(autoreset=True)

# Header default
DEFAULT_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,id;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://quest.arenavs.com',
    'referer': 'https://quest.arenavs.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site'
}

# Daftar tugas
TASKS = {
    1: {"name": "Follow Twitter", "reward": 30000},
    2: {"name": "Like & Retweet", "reward": 14000},
    3: {"name": "Invite Friends", "reward": 30000},
    4: {"name": "Join Discord", "reward": 20000}
}

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log_message(message, color=Fore.WHITE):
    """Mencetak log dengan format yang rapi."""
    print(f"{Fore.LIGHTBLACK_EX}[{get_timestamp()}]{Fore.WHITE} {color}{message}")

def generate_wallet():
    """Membuat wallet baru."""
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return private_key, acct.address

def get_random_proxy(proxies):
    """Mengambil proxy secara acak."""
    return random.choice(proxies) if proxies else None

def send_request(url, headers, data=None, proxy=None, method="POST"):
    """Mengirim request HTTP dengan proxy & error handling."""
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=10)
        else:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def register_wallet(wallet_address, referral_code, proxy, user_agent):
    """Mendaftarkan wallet baru."""
    url = "https://quest-api.arenavs.com/api/v1/users/initialize"
    headers = DEFAULT_HEADERS.copy()
    headers['user-agent'] = user_agent
    data = {"walletAddress": wallet_address, "referralCode": referral_code}
    
    return send_request(url, headers, data, proxy)

def complete_task(user_id, task_id, token, proxy, user_agent):
    """Menyelesaikan task."""
    url = f"https://quest-api.arenavs.com/api/v1/tasks/{task_id}/complete/{user_id}"
    headers = DEFAULT_HEADERS.copy()
    headers['user-agent'] = user_agent
    headers['authorization'] = f'Bearer {token}'
    
    return send_request(url, headers, {}, proxy)

def get_user_data(wallet_address, token, proxy, user_agent):
    """Mengambil data pengguna."""
    url = f"https://quest-api.arenavs.com/api/v1/users/{wallet_address}"
    headers = DEFAULT_HEADERS.copy()
    headers['user-agent'] = user_agent
    headers['authorization'] = f'Bearer {token}'
    
    return send_request(url, headers, method="GET", proxy=proxy)

def save_account_data(user_id, private_key, wallet_address, referral_code, xp):
    """Menyimpan data akun ke file."""
    with open('accounts.txt', 'a') as f:
        f.write(f"User ID: {user_id}\n")
        f.write(f"Private Key: {private_key}\n")
        f.write(f"Address: {wallet_address}\n")
        f.write(f"Referral Code: {referral_code}\n")
        f.write(f"XP: {xp}\n")
        f.write(f"{'=' * 60}\n\n")

def process_registration(wallet_num, referral_code, proxies):
    """Proses registrasi 1 akun."""
    private_key, wallet_address = generate_wallet()
    proxy = get_random_proxy(proxies)
    user_agent = UserAgent().chrome
    
    reg_response = register_wallet(wallet_address, referral_code, proxy, user_agent)
    
    if "error" in reg_response or "user" not in reg_response:
        return f"[{wallet_num}] Registration failed", False

    user_id = reg_response['user']['id']
    token = reg_response['token']
    refcode = reg_response['user']['referralCode']
    
    # Selesaikan tugas
    for task_id, task_info in TASKS.items():
        complete_task(user_id, task_id, token, proxy, user_agent)
    
    user_data = get_user_data(wallet_address, token, proxy, user_agent)
    xp = user_data.get('xp', 0) if user_data else 0
    save_account_data(user_id, private_key, wallet_address, refcode, xp)

    return f"[{wallet_num}] Registered {wallet_address} (XP: {xp})", True

def main():
    print(f"{Fore.YELLOW}{'='*40}")
    print(f"      AUTO REFERRAL BOT (MULTI-THREAD)      ")
    print(f"{'='*40}{Style.RESET_ALL}")
    
    proxies = []
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        log_message("No proxies found, continuing without proxies", Fore.YELLOW)
    
    referral_code = input(f"{Fore.YELLOW}Enter your referral code: {Style.RESET_ALL}")
    num_refs = int(input(f"{Fore.YELLOW}Enter number of referrals: {Style.RESET_ALL}"))
    max_threads = int(input(f"{Fore.YELLOW}Enter max threads (default 5): {Style.RESET_ALL}") or 5)

    print(f"\n{Fore.CYAN}Starting registration with {num_refs} referrals...{Style.RESET_ALL}\n")
    
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(process_registration, i+1, referral_code, proxies): i+1 for i in range(num_refs)}
        
        with tqdm(total=num_refs, desc="Progress", unit="acc") as pbar:
            for future in as_completed(futures):
                result, success = future.result()
                log_message(result, Fore.GREEN if success else Fore.RED)
                pbar.update(1)

    log_message(f"Process completed! Total referrals: {num_refs}", Fore.GREEN)

if __name__ == "__main__":
    main()
