import socket
import threading
import time
import argparse
import matplotlib.pyplot as plt
from utils import *

parser = argparse.ArgumentParser(description="UDP Pose Receiver and Visualizer")
parser.add_argument("--point_cloud", type=str, required=True, help="Path to the point cloud file (e.g., points3D.txt)")
parser.add_argument("--plot_interval", type=float, default=0.5, help="設定繪圖更新頻率 (單位：秒)，預設為 0.5 秒")
parser.add_argument("--udp_port", type=int, default=8888, help="UDP port listening to. Default=8888")
args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", args.udp_port))
print(f"Listening Port {args.udp_port}...")

cam_poses = []
points3D_fname = args.point_cloud

# 加入一個 Lock 確保多執行緒同時讀寫 cam_poses 時的安全
pose_lock = threading.Lock()

# ==========================================
# 1. 建立專門接收 UDP 資料的背景函式
# ==========================================
def receive_data():
    global cam_poses
    print(">>> [Debug] Receiver thread started successfully!", flush=True)
    while True:
        try:
            # 這裡會持續等待並接收封包，不會被畫圖影響
            data, addr = sock.recvfrom(1024) 

            print(f">>> [Debug] Received raw packet from {addr}", flush=True)
            
            message = data.decode('utf-8').split('|')
            img_stamp = message[0]
            time_stamp = message[1]
            q, t = parse_arpose(message[2])
            sampled_fused_pose = Pose(q, t)

            # 寫入共用陣列時稍微鎖住一下
            with pose_lock:
                cam_poses.append((sampled_fused_pose, 'blue'))

            # 持續即時印出資訊
            print(f"Image Stamp: {img_stamp} | Time: {time_stamp}")
            print(f"Current Pose: {sampled_fused_pose}")
            
        except Exception as e:
            print(f">>> [Receiver Error] 發生錯誤: {e}", flush=True)

# 啟動背景執行緒
receiver_thread = threading.Thread(target=receive_data, daemon=True)
receiver_thread.start()

# ==========================================
# 2. 主執行緒專心處理 Matplotlib 繪圖
# ==========================================
plt.ion()
fig = plt.figure()
ax = fig.add_subplot()  # 2d

# 效能優化小提醒：點雲檔案建議只在迴圈外讀取一次，不要每次畫圖都重新 load
pt_cloud = load_point_cloud(points3D_fname)

while True:
    try:
        with pose_lock:
            # 複製一份當下的 poses 狀態來畫圖，避免畫圖到一半背景執行緒又塞新資料進來
            current_poses = list(cam_poses)
        
        if not current_poses:
            time.sleep(0.1) 
            continue
        
        # display_pose(fig, ax, current_poses, pt_cloud, only_pos=False)
        display_pose_2d(fig, ax, current_poses, pt_cloud, only_pos=False)
        
        # 會讓迴圈暫停指定的秒數，還會同時刷新 matplotlib 的 GUI 畫面，避免視窗無回應
        plt.pause(args.plot_interval)
        
    except KeyboardInterrupt:
        print("Local Device Terminated.")
        break
    except Exception as e:
        print("Plot Error: ", e)
        time.sleep(1)