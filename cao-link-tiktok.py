import requests
import json
import time
from datetime import datetime
import os

# Hàm tải file về từ URL
def download_file(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        return True
    return False

# Hàm upload file lên Imgur và lấy link
def upload_to_imgur(file_path):
    url = 'https://api.imgur.com/3/upload'
    headers = {'Authorization': 'Client-ID 6b7b6a54fc39b5f'}  # Sử dụng Client ID của bạn
    with open(file_path, 'rb') as file:
        files = {'image': file}
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            response_data = response.json()
            return response_data['data']['link']
        else:
            print(f"❌ Lỗi upload lên Imgur: {response.status_code}")
            print(f"Nội dung phản hồi: {response.text}")
            return None

# Hàm lấy dữ liệu từ TikTok API
def get_data(link):
    try:
        api_url = f"https://anhcode.click/anhcode/api/dltt.php?url={link}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('code') == 0:
            return data['data']
        else:
            print(f"❌ API lỗi: {data.get('msg')}")
            return None
    except Exception as e:
        print(f"❌ Lỗi khi cào: {str(e)}")
        return None

def main():
    # --- Bước 1: Nhập danh sách link ---
    print("Nhập danh sách link TikTok, mỗi link 1 dòng. Gõ 'xong' để kết thúc.")
    links = []
    while True:
        link = input()
        if link.lower() == 'xong':
            break
        if link.strip():
            links.append(link.strip())

    if not links:
        print("⚠️ Bạn chưa nhập link nào. Thoát...")
        return

    # --- Bước 2: Hỏi trường cần cào ---
    field = ""
    while not field:
        print("\ntitle = tiêu đề,\n play = video ko logo,\n music = nhạc,\n cover = ảnh bìa, etc.): ")
        field = input("\nBạn muốn cào mục nào? (ví dụ: title, play, music, cover, etc.): ").strip()
        if not field:
            print("⚠️ Bạn phải nhập tên mục!")

    # --- Bước 3: Hỏi dạng lưu ---
    format_choice = ""
    while format_choice not in ['txt', 'json']:
        format_choice = input("\nBạn muốn lưu dạng nào? (txt/json): ").strip().lower()
        if format_choice not in ['txt', 'json']:
            print("⚠️ Chỉ được chọn 'txt' hoặc 'json'!")

    # Tạo tên file tự động
    now = datetime.now()
    time_str = now.strftime("%H_%M_%S-%d_%m_%Y")  # giờ_phút_giây-ngày_tháng_năm
    time_str = time_str.replace('/', '-')  # Thay thế dấu '/' bằng dấu '-' để tránh lỗi
    file_name = f"LAMDev-{time_str}.{format_choice}"


    # --- Bắt đầu cào dữ liệu ---
    print(f"\n🔎 Bắt đầu cào '{field}' từ {len(links)} link...")

    results = []
    for idx, link in enumerate(links, 1):
        data = get_data(link)
        if data:
            value = data.get(field)
            if value is not None:
                # Tải các file nếu cần thiết (cover, play, avatar)
                if field in ['cover', 'play', 'avatar']:
                    file_url = value
                    file_extension = '.jpg' if field in ['cover', 'avatar'] else '.mp4'
                    file_name_local = f"{field}-{idx}{file_extension}"

                    # Tải file
                    download_file(file_url, file_name_local)

                    # Upload lên Imgur
                    file_link = upload_to_imgur(file_name_local)
                    if file_link:
                        results.append(file_link)
                        print(f"[{idx}/{len(links)}] ✅ Link {field} đã được upload: {file_link}")
                    else:
                        print(f"[{idx}/{len(links)}] ⚠️ Không thể upload file {field}")
                    os.remove(file_name_local)  # Xóa file sau khi upload
                else:
                    results.append(str(value))
                    print(f"[{idx}/{len(links)}] ✅ {value}")
            else:
                print(f"[{idx}/{len(links)}] ⚠️ Không tìm thấy mục '{field}' trong link này")
        else:
            print(f"[{idx}/{len(links)}] ❌ Không lấy được dữ liệu cho link này")
        time.sleep(0.5)  # chống spam server

    # --- Lưu file ---
    if format_choice == 'txt':
        with open(file_name, "w", encoding="utf-8") as f:
            for item in results:
                f.write(item + "\n")
    elif format_choice == 'json':
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Đã lưu {len(results)} kết quả vào file: {file_name}")

if __name__ == "__main__":
    main()
