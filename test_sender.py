import socket
import time

# 設定為全局廣播地址
UDP_IP = "255.255.255.255" 
UDP_PORT = 8888
TARGET_FPS = 30  # 目標幀率

print(f"準備發送廣播測試資料到 {UDP_IP}:{UDP_PORT}...")
print(f"模擬發送頻率: 每秒 {TARGET_FPS} 幀")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

counter = 0
# 計算每發送一筆資料需要等待的時間
frame_interval = 1.0 / TARGET_FPS 

while True:
    # 紀錄這一個迴圈的開始時間，用來扣掉發送資料消耗的時間，讓頻率更精準
    start_time = time.time()
    
    test_message = f"img_{counter}|{time.time()}|0.0 0.0 0.0 1.0 1.0 2.0 3.0"
    
    try:
        # 發送廣播
        sock.sendto(test_message.encode('utf-8'), (UDP_IP, UDP_PORT))
        
        # 為了避免終端機被洗版導致程式變慢，我們改成每秒(每29幀)只印出一次提示
        if counter % TARGET_FPS == 0:
            print(f"已發送 {counter} 筆資料... 最新廣播: {test_message}")
            
    except Exception as e:
        print(f"發送失敗: {e}")
    
    counter += 1
    
    # 計算這個迴圈實際花了多少時間，並動態調整 sleep 的長度
    process_time = time.time() - start_time
    sleep_time = frame_interval - process_time
    
    if sleep_time > 0:
        time.sleep(sleep_time)