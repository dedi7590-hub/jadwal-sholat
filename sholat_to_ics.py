import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def generate_prayer_ics():
    # 1. Konfigurasi Parameter API
    tahun = datetime.now().year
    bulan = datetime.now().month
    
    local_tz = ZoneInfo("Asia/Jakarta")
    utc_tz = ZoneInfo("UTC")
    
    # Menggunakan Aladhan API untuk wilayah Jakarta (Method 5 = Kemenag RI)
    url = f"https://api.aladhan.com/v1/calendarByCity/{tahun}/{bulan}"
    params = {
        "city": "Jakarta",
        "country": "Indonesia",
        "method": 5 
    }

    print(f"Mengambil data jadwal sholat untuk {bulan}/{tahun}...")
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Gagal mengambil data API. Status code: {response.status_code}")
        return

    data = response.json()["data"]

    # 2. Inisialisasi Objek Kalendar iCal
    cal = Calendar()
    cal.add('prodid', '-//Jadwal Sholat Jakarta Selatan iCal Generator//id//')
    cal.add('version', '2.0')

    target_sholats = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    nama_id = {
        'Fajr': 'Subuh',
        'Dhuhr': 'Dzuhur',
        'Asr': 'Ashar',
        'Maghrib': 'Maghrib',
        'Isha': 'Isya'
    }

    # 3. Iterasi setiap hari dari data API
    for hari in data:
        tanggal_str = hari['date']['gregorian']['date'] # Format: DD-MM-YYYY
        timings = hari['timings']

        for sholat in target_sholats:
            if sholat in timings:
                waktu_raw = timings[sholat].split(' ')[0] 
                
                # Buat waktu lokal WIB
                dt_str = f"{tanggal_str} {waktu_raw}"
                dt_local = datetime.strptime(dt_str, "%d-%m-%Y %H:%M").replace(tzinfo=local_tz)
                
                # Konversi waktu lokal ke UTC agar Google Calendar membacanya dengan presisi mutlak
                dt_start_utc = dt_local.astimezone(utc_tz)
                dt_end_utc = dt_start_utc + timedelta(minutes=10)

                # Buat Event Kalender
                event = Event()
                event.add('summary', f"Sholat {nama_id[sholat]}")
                event.add('dtstart', dt_start_utc)
                event.add('dtend', dt_end_utc)
                event.add('description', f"Waktu sholat {nama_id[sholat]} untuk wilayah Jakarta Selatan.")
                
                cal.add_component(event)

    # 4. Simpan ke dalam file .ics
    nama_file = "jadwal_sholat_jakarta_selatan.ics"
    with open(nama_file, 'wb') as f:
        f.write(cal.to_ical())

    print(f"Berhasil! File iCal tersimpan dengan nama: {nama_file}")

if __name__ == "__main__":
    generate_prayer_ics()
