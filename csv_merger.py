import glob
import os

# Mengambil path direktori di mana program dijalankan
directory_path = os.getcwd()

# Mencari semua file CSV dalam direktori yang sama dengan program ini dijalankan
csv_files = glob.glob(os.path.join(directory_path, "*.csv"))

# List untuk menampung data dari setiap file CSV
combined_lines = []

# Membaca setiap file CSV dan menggabungkan setiap baris
for file_path in csv_files:
    try:
        # Membaca file sebagai teks
        with open(file_path, 'r', encoding='utf-8') as file:
            # Membaca semua baris dan menambahkannya ke dalam list
            lines = file.readlines()
            combined_lines.extend([line.strip() for line in lines])  # Menghapus spasi dan newline
    except Exception as e:
        print(f"Terjadi kesalahan saat membaca file {file_path}: {e}")

# Menyimpan data yang sudah digabungkan ke dalam file CSV baru
output_path = os.path.join(directory_path, "combined_output.csv")
with open(output_path, 'w', encoding='utf-8') as output_file:
    for line in combined_lines:
        output_file.write(f"{line}\n")

print(f"Data berhasil digabungkan dan disimpan di {output_path}")
