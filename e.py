import os
import json
import time
import requests
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Inisialisasi Colorama untuk auto-reset warna setelah setiap print
init(autoreset=True)

# Fungsi untuk menampilkan pesan sambutan
def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop  Electra App")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop")

# Fungsi untuk memuat akun dari file
def load_accounts():
    with open('data.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Fungsi untuk membuat headers HTTP
def get_headers(init_data):
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://tg-app-embed.electra.trade',
        'pragma': 'no-cache',
        'referer': 'https://tg-app-embed.electra.trade/',
        'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129", "Microsoft Edge WebView2";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
        'x-telegram-init-data': init_data
    }

# Fungsi untuk mengecek apakah farming telah berakhir
def check_farming_end(time_of_guess, farming_duration_minutes=6):
    current_time = int(time.time() * 1000)
    elapsed_time = (current_time - time_of_guess) / 1000 / 60
    return elapsed_time >= farming_duration_minutes

# Fungsi untuk memulai farming baru
def start_new_farming(headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'
    
    try:
        # Mendapatkan harga BTC saat ini
        btc_price_response = requests.get(f'{base_url}/btcPrice', headers=headers)
        btc_price = float(btc_price_response.json().get('price', 0))
        current_time = int(time.time() * 1000)
        farming_type = random.choice(["down", "up"])
        
        farming_data = {
            "guess": {
                "type": farming_type,
                "btcPrice": btc_price,
                "duration": 6,
                "timeOfGuess": current_time,
                "pointsToWin": 1200
            }
        }

        # Memulai farming baru
        requests.post(f'{base_url}/startFarming', headers=headers, json=farming_data)
        print(Fore.GREEN + f"Farming baru dimulai dengan tipe '{farming_type}' dengan harga BTC: {btc_price}")
    
    except Exception as e:
        print(Fore.RED + f"Error saat memulai farming baru: {str(e)}")

# Fungsi untuk mengupdate status aktivitas pengguna terakhir
def update_user_last_active(headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'
    
    try:
        response = requests.get(f'{base_url}/updateUserLastActive', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(Fore.GREEN + f"Status aktivitas terakhir pengguna {user_data.get('username', 'Tidak Diketahui')} berhasil diperbarui.")
            return user_data  # Return the updated user data
        else:
            print(Fore.RED + f"Gagal memperbarui status aktivitas terakhir: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat memperbarui status aktivitas terakhir: {str(e)}")
        return None

# Fungsi untuk mengupdate streak jika hadiah harian belum diklaim
def claim_daily_reward(user_data, headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'


    # Cek apakah ada streak yang belum diklaim
    daily_streak = user_data.get('daily_streak', [])
    if not daily_streak:
        print(Fore.YELLOW + "Tidak ada data streak harian.")
        return

    last_streak = daily_streak[-1] if daily_streak else None

    if last_streak and not last_streak['claimed']:
        try:
            # Ambil daftar reward dari settings
            response = requests.get(f'{base_url}/settings', headers=headers)
            if response.status_code == 200:
                settings_data = response.json()
                reward_list = settings_data.get('DAILY_REWARD_LIST', [])

                # Panjang streak harian
                user_streak = len(daily_streak)
                reward = reward_list[user_streak - 1] if user_streak <= len(reward_list) else reward_list[-1]

                # Update streak dan klaim hadiah
                streak_data = {
                    "daily_streak": daily_streak,
                    "userStreak": user_streak,
                    "reward": reward
                }

                response = requests.post(f'{base_url}/updateStreak', headers=headers, json=streak_data)
                if response.status_code == 200:
                    print(Fore.GREEN + f"Hadiah harian sebesar {reward} berhasil diklaim.")
                else:
                    print(Fore.RED + f"Error saat klaim hadiah harian: {response.status_code}")
            else:
                print(Fore.RED + f"Gagal mendapatkan pengaturan: {response.status_code}")
        except Exception as e:
            print(Fore.RED + f"Error saat memanggil pengaturan: {str(e)}")
    else:
        if last_streak and last_streak['claimed']:
            print(Fore.YELLOW + "Hadiah harian sudah diklaim.")
        else:
            print(Fore.YELLOW + "Tidak ada data streak yang valid untuk diklaim.")

# Fungsi untuk mencetak data pengguna yang penting
def print_user_data(user_data):
    username = user_data.get('username', 'Tidak Diketahui')
    points = user_data.get('points', 0)
    daily_streak = user_data.get('daily_streak', [])

    print(Fore.CYAN + f"Data Pengguna {username}:")
    print(f"  Poin: {points}")
    print(f"  Streak Harian: {len(daily_streak)} hari")

# Fungsi untuk mendapatkan tugas dari settings jika tidak ada di userData
def get_tasks_from_settings(headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'
    try:
        response = requests.get(f'{base_url}/settings', headers=headers)
        if response.status_code == 200:
            settings_data = response.json()
            task_list = settings_data.get('TASK_LIST', [])
            print(Fore.GREEN + "Berhasil mengambil tugas.")
            return task_list
        else:
            print(Fore.RED + f"Error saat mengambil tugas: {response.status_code}")
            return []
    except Exception as e:
        print(Fore.RED + f"Error saat memanggil tugas: {str(e)}")
        return []

# Fungsi untuk memverifikasi dan menyelesaikan tugas
def verify_and_complete_task(task_id, headers, base_url):
    try:
        print(Fore.YELLOW + f"Memverifikasi tugas '{task_id}'...")
        verification_payload = {
            "task_id": task_id,
            "status": "verification_in_progress"
        }
        verification_response = requests.post(
            f"{base_url}/taskProcess", headers=headers, json=verification_payload
        )

        if verification_response.status_code == 200:
            print(Fore.GREEN + f"Tugas '{task_id}' berhasil diverifikasi.")
        else:
            print(Fore.RED + f"Verifikasi gagal untuk '{task_id}': {verification_response.status_code}")
            return  # Berhenti jika verifikasi gagal


        complete_task(task_id, headers, base_url)
    except Exception as e:
        print(Fore.RED + f"Error saat memverifikasi tugas '{task_id}': {str(e)}")

# Fungsi untuk menandai tugas sebagai selesai
def complete_task(task_id, headers, base_url):
    try:
        print(Fore.YELLOW + f"Menyelesaikan tugas '{task_id}'...")
        done_payload = {
            "task_id": task_id,
            "status": "done"
        }
        done_response = requests.post(
            f"{base_url}/taskProcess", headers=headers, json=done_payload
        )

        if done_response.status_code == 200:
            print(Fore.GREEN + f"Tugas '{task_id}' berhasil diselesaikan.")
        else:
            print(Fore.RED + f"Gagal menyelesaikan tugas '{task_id}': {done_response.status_code}")
    except Exception as e:
        print(Fore.RED + f"Error saat menyelesaikan tugas '{task_id}': {str(e)}")


# Fungsi untuk memproses daftar tugas
def process_task_list(tasks, headers, base_url):
    print(Fore.GREEN + "Daftar Tugas:")
    for task_id, task_info in tasks.items():
        title = task_info.get('title', task_id)  # Ambil judul atau gunakan ID sebagai fallback
        status = task_info.get('status')

        print(Fore.YELLOW + f"Memproses Tugas: {title} (Status: {status})")


        if status == 'done':
            print(Fore.GREEN + f"Tugas '{title}' sudah selesai.")
        elif status == 'verification_in_progress':
            complete_task(task_id, headers, base_url)
        else:
            verify_and_complete_task(task_id, headers, base_url)

# Fungsi untuk menangani hasil farming dan mereset farming
def handle_farming_result_and_reset(user_data, headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'

    try:
        farming_data = user_data.get('guess')
        if farming_data is None:
            print(Fore.YELLOW + "Tidak ada data farming ditemukan.")
            return

        time_of_guess = farming_data['timeOfGuess']
        if check_farming_end(time_of_guess):
            print(Fore.YELLOW + "Waktu farming telah berakhir. Memeriksa hasil...")

            btc_price_response = requests.get(f'{base_url}/guessBtcPrice', headers=headers)
            if btc_price_response.status_code != 200:
                print(Fore.RED + "Gagal mengambil harga BTC.")
                return
            btc_prices = btc_price_response.json()
            price_before = float(btc_prices['priceBefore'])
            price_after = float(btc_prices['priceAfter'])

            guess_type = farming_data['type']
            if (guess_type == "down" and price_before > price_after) or (guess_type == "up" and price_before < price_after):
                print(Fore.GREEN + f"Menang dengan prediksi '{guess_type}'!")
                reset_payload = {"pointsToWin": 2400, "winStreak": 1}
            else:
                print(Fore.RED + f"Kalah dengan prediksi '{guess_type}'.")
                reset_payload = {"pointsToWin": 1200, "winStreak": 0}

            reset_farming_response = requests.post(f'{base_url}/resetFarming', headers=headers, json=reset_payload)
            if reset_farming_response.status_code == 200:
                print(Fore.GREEN + "Farming berhasil di-reset.")
                # Memulai farming baru setelah reset berhasil
                start_new_farming(headers)
            else:
                print(Fore.RED + f"Error saat mereset farming: {reset_farming_response.status_code}")
        else:
            print(Fore.YELLOW + "Waktu farming belum berakhir.")
    except Exception as e:
        print(Fore.RED + f"Error saat menangani hasil farming: {str(e)}")

# Fungsi utama untuk memproses akun
def process_account(init_data):
    headers = get_headers(init_data)
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'

    try:
        user_data_response = requests.get(f'{base_url}/userData', headers=headers)
        user_data = user_data_response.json().get('user', {})
        print(Fore.CYAN + f"Memproses akun: {user_data.get('username', 'Tidak Diketahui')}")


        # Update status aktivitas terakhir
        updated_user_data = update_user_last_active(headers)
        if updated_user_data:
            user_data = updated_user_data  # Use the updated data for further processing

        # Cetak data pengguna yang penting
        print_user_data(user_data)

        # Jika farming sudah dimulai, cek hasilnya
        if user_data.get('farming_started'):
            handle_farming_result_and_reset(user_data, headers)
        else:
            start_new_farming(headers)

        # Jika hadiah harian belum diklaim, klaim hadiahnya
        if not user_data.get('daily_reward_claimed'):
            claim_daily_reward(user_data, headers)
        else:
            print(Fore.GREEN + "Hadiah harian sudah diklaim.")

        # Proses tugas pengguna
        tasks = user_data.get('tasks', {})
        if not tasks:
            tasks_from_settings = get_tasks_from_settings(headers)
            tasks = {task['id']: task for task in tasks_from_settings} if tasks_from_settings else {}

        if tasks:
            process_task_list(tasks, headers, base_url)

        print(Fore.GREEN + f"Akun {user_data.get('username', 'Tidak Diketahui')} berhasil diproses.")
    except Exception as e:
        print(Fore.RED + f"Error saat memproses akun: {str(e)}")

# Fungsi utama untuk menjalankan program
def main():
    print_welcome_message()
    accounts = load_accounts()
    total_accounts = len(accounts)
    print(Fore.CYAN + f"Total akun: {total_accounts}")


    while True:
        for index, init_data in enumerate(accounts, 1):
            try:
                print(Fore.MAGENTA + f"\nMemproses akun {index}/{total_accounts}")
                process_account(init_data)
                if index < total_accounts:
                    print(Fore.YELLOW + "Menunggu 5 detik sebelum memproses akun berikutnya...")
                    time.sleep(5)
            except Exception as e:
                print(Fore.RED + f"Error saat memproses akun ke-{index}: {str(e)}")

        print(Fore.GREEN + "\nSemua akun telah diproses.")

        countdown_time = timedelta(hours=6)
        start_time = datetime.now()
        while (datetime.now() - start_time) < countdown_time:
            remaining_time = countdown_time - (datetime.now() - start_time)
            hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"\rWaktu tersisa: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
            time.sleep(1)

        print(Fore.GREEN + "\nMemulai ulang proses...")

if __name__ == "__main__":
    main()
