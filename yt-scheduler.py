import schedule
import time
import asyncio
import os
from yt_video_comment_getter import get_video_comments
import datetime
from datetime import timedelta
async def process_line(line):
    print(f"Memproses: {line.strip()}")
    try:
        await get_video_comments(line)
        print(f"Selesai memproses: {line.strip()}")
    except Exception as e:
        print(f"Exception terjadi pada get_video_comments(): {e}")
        raise SystemExit("Hentikan program dan lanjutkan keesokan harinya")
    
async def process_file(filename):
    temp_filename = f"{filename}.temp"
    
    with open(filename, 'r') as file, open(temp_filename, 'w') as temp_file:
        lines = file.readlines()
        if lines:
            await process_line(lines[0])
            temp_file.writelines(lines[1:])
        else:
            print("File kosong atau semua tugas telah selesai.")
    
    os.replace(temp_filename, filename)

def start_processing():
    try:
        asyncio.run(process_file('tasks.txt'))
    except SystemExit as e:
        print(f"Program dihentikan: {e}")
        # Jadwalkan ulang untuk keesokan harinya
        tomorrow = datetime.now() + timedelta(days=1)
        next_run = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        schedule.clear()
        schedule.every().day.at(next_run.strftime("%H:%M")).do(start_processing)
        print(f"Program akan dilanjutkan pada: {next_run}")

# Jadwalkan pemrosesan file setiap hari pada pukul 10:00
schedule.every().day.at("10:00").do(start_processing)


# Loop utama untuk menjalankan scheduler
while True:
    schedule.run_pending()
    time.sleep(1)

