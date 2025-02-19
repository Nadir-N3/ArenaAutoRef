# Auto Referral Bot (Multi-Threading)

Bot otomatis untuk melakukan pendaftaran akun dengan sistem referal pada **ArenaVS Quest**.  
Menggunakan **multi-threading** agar lebih cepat dan **tampilan interaktif** dengan **progress bar**.

## ✨ Fitur
✅ **Multi-threading** → Bisa daftar banyak akun sekaligus lebih cepat  
✅ **Progress bar (tqdm)** → Menampilkan progress secara visual  
✅ **Tampilan lebih rapi** → Output lebih bersih, log lebih jelas  
✅ **Error handling lebih baik** → Jika ada error di satu akun, proses lainnya tetap berjalan  

---

## 📦 Instalasi

1. **Clone Repository**
   ```sh
   git clone https://github.com/Yuurichan-N3/ArenaAutoRef.git
   cd ArenaAutoRef

2. Install Dependencies

```sh
pip install -r requirements.txt
```



---

## ⚙️ Cara Penggunaan

1. Siapkan File Proxy (Optional)
Buat file proxy.txt dan masukkan daftar proxy (1 proxy per baris). Jika tidak ada, bot tetap bisa berjalan tanpa proxy.


2. Jalankan Script

python bot.py


3. Masukkan Inputan

Referral Code → Masukkan kode referal

Jumlah Referral → Tentukan jumlah akun yang ingin didaftarkan

Jumlah Thread (Opsional) → Default 5 (bisa diubah untuk kecepatan lebih tinggi)



4. Proses Otomatis Berjalan

Akun akan dibuat secara otomatis

Bot akan menyelesaikan tugas-tugas yang tersedia

Data akun akan tersimpan di accounts.txt





---

## 📄 Format Output (accounts.txt)

Setiap akun yang berhasil dibuat akan disimpan dalam format berikut:

User ID: 123456
Private Key: 0xabc123...
Address: 0xwallet123...
Referral Code: REF12345
XP: 100000
============================================================


---

## 🔧 Konfigurasi

Max Threads → Bisa disesuaikan agar lebih cepat, tapi jangan terlalu tinggi agar tidak terkena limit.

Proxy → Gunakan proxy untuk keamanan dan menghindari rate limit.



---

## 🛠 Dependencies

Python 3.8+

requests

eth_account

fake_useragent

colorama

tqdm


Install semua dependencies dengan:

pip install -r requirements.txt


---

## 📜 Lisensi  

Script ini didistribusikan untuk keperluan pembelajaran dan pengujian. Penggunaan di luar tanggung jawab pengembang.  

Untuk update terbaru, bergabunglah di grup **Telegram**: [Klik di sini](https://t.me/sentineldiscus).


---

## 💡 Disclaimer
Penggunaan bot ini sepenuhnya tanggung jawab pengguna. Kami tidak bertanggung jawab atas penyalahgunaan skrip ini.
