import numpy as np
import cv2
from godirect import GoDirect
import time
import os
import csv
import pygame

def create_base_frame(screen_width, screen_height, inner_frame_size, frame_margin_x, frame_margin_y, image=None):
    
    frame = np.ones((screen_height, screen_width, 3), dtype=np.uint8) * 255  # 흰색 프레임
    inner_frame = np.ones((inner_frame_size, inner_frame_size, 3), dtype=np.uint8) * 255 # 흰색 프레임
    
    if image is not None:
        image_frame_size = inner_frame_size - 50
        image_frame = np.zeros((image_frame_size, image_frame_size, 3), dtype=np.uint8)
        img = cv2.resize(image, (image_frame_size, image_frame_size))
        x_offset = (image_frame_size - img.shape[1]) // 2
        y_offset = (image_frame_size - img.shape[0]) // 2
        image_frame[y_offset:y_offset + img.shape[0], x_offset:x_offset + img.shape[1]] = img
        inner_margin = (inner_frame_size - image_frame_size) // 2
        inner_frame[inner_margin:inner_margin + image_frame_size, inner_margin:inner_margin + image_frame_size] = image_frame

    frame[frame_margin_y:frame_margin_y + inner_frame_size, frame_margin_x:frame_margin_x + inner_frame_size] = inner_frame
    cv2.rectangle(frame, (frame_margin_x, frame_margin_y), (frame_margin_x+ inner_frame_size,frame_margin_y+inner_frame_size), (0,0,0), 5)
    return frame
    
def overlay_text(frame, text, position, font_scale=1, color=(0, 0, 0), thickness=2):
    """
    Overlay text on a frame at the specified position.
    """
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
    return frame

# 점 위치 계산 (사각형 변을 따라 움직임)
def get_dot_position(inner_start, inner_size, elapsed_time, total_time_per_side):
    total_cycle_time = 4 * total_time_per_side
    t = elapsed_time % total_cycle_time

    if t < total_time_per_side:  # 상단
        x = int(inner_start[0] + t / total_time_per_side * inner_size)
        y = inner_start[1] 
    elif t < 2 * total_time_per_side:  # 우측
        x = inner_start[0] + inner_size 
        y = int(inner_start[1] + (t - total_time_per_side) / total_time_per_side * inner_size)
    elif t < 3 * total_time_per_side:  # 하단
        x = int(inner_start[0] + inner_size - (t - 2 * total_time_per_side) / total_time_per_side * inner_size)
        y = inner_start[1] + inner_size
    else:  # 좌측
        x = inner_start[0] 
        y = int(inner_start[1] + inner_size - (t - 3 * total_time_per_side) / total_time_per_side * inner_size)
    return x, y

def calculate_frame_margin(outer_size, inner_size):
    return (outer_size - inner_size) // 2

# CSV 파일명 설정
csv_file_name =  os.path.join('./data', input("Enter the CSV file name (with .csv extension): ").strip())
os.makedirs(os.path.dirname(csv_file_name), exist_ok=True)
    
    
godirect = GoDirect()
print("Initializing GoDirect...")
device = godirect.get_device()
# GoDirect 장치 연결 확인
if not (device and device.open(auto_start=False)):
    raise RuntimeError("Failed to connect to GoDirect device")

bgm_path = './content/bgm.mp3'
device.enable_sensors([1]) # 센서 ID를 환경에 맞게 수정 필요
device.start()

folders = ['./content/head', './content/leftarm', './content/rightarm', './content/leftleg', './content/rightleg', './content/spine']

#폴더별 이미지 로드
section_images = {}
for folder in folders:
    images = []
    if os.path.exists(folder):
        for file_name in sorted(os.listdir(folder), key=lambda x: int(x.split('.')[0])):
            images.append(cv2.imread(os.path.join(folder,file_name)))
    section_images[folder] = images
        
# 윈도우 설정
window_name = "Breathing Animation"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

screen_width = cv2.getWindowImageRect(window_name)[2]
screen_height = cv2.getWindowImageRect(window_name)[3]

inner_frame_size = 600 # 내부 프레임
frame_margin_x = calculate_frame_margin(screen_width, inner_frame_size)
frame_margin_y = calculate_frame_margin(screen_height, inner_frame_size)

# 초기화 변수
initialization_time = 20 # 초기화 시간 (초)
initial_start_time = time.time()
initializing = True
measuring_level = False
force_min = None

force_max = None
BGM_STARTED = False

# 호흡 주기 관련 변수
cycle_start_time = None
cycle_detected = False
cycle_times = []
avg_cycle_time = 4.0 # 기본 값값
recommended_cycle_time = 0
cycle_status = "Waiting.."

# CSV 파일 열기
with open(csv_file_name, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    # 헤더 작성
    csv_writer.writerow(["Timestamp", "Force Value"])

    try:
        while True:
            # 센서 데이터 읽기
            if device.read():
                sensor = device.get_enabled_sensors()[0]
                if len(sensor.values) > 0:
                    force = sensor.values[0]
                    sensor.clear()
                    # print(f"force value: {force}")
                    timestamp = time.time()
                    # CSV에 데이터 저장
                    csv_writer.writerow([timestamp, force])
                    csv_file.flush()

                    # 초기화 모드
                    if initializing:
                        elapsed_time = time.time() - initial_start_time
                        if elapsed_time < initialization_time:
                            frame = create_base_frame(screen_width, screen_height, inner_frame_size, frame_margin_x, frame_margin_y, image=cv2.imread('./content/head/1.jpg'))
                            frame = overlay_text(frame, 'Initialization...', (frame_margin_x + 20, frame_margin_y -30))
                            frame = overlay_text(frame, f'Your force is {round(force, 3)}', (frame_margin_x + 20, inner_frame_size + frame_margin_y + 50))
                            cv2.imshow(window_name, frame)

                            if force_min is None or force < force_min:
                                force_min = force
                            if force_max is None or force > force_max:
                                force_max = force
                        else:
                            initializing = False
                            measuring_level = True
                            level_start_time = time.time()
                            print("Initialization complete")
                                    
                        
                    elif measuring_level:
                        elapsed_time = time.time() - level_start_time
                        
                        images = section_images['./content/rightarm']
                        normalized_force = np.clip(
                            (force - force_min) / (force_max - force_min) * (len(images) - 1), 0, len(images) - 1
                        )
                        level = int(normalized_force)
                        
                        current_image = images[level]
                        threshold = force_min + (force_max - force_min) * 0.1
                        
                        
                        if not cycle_detected and force > threshold:
                            cycle_status = "Cycle Start"
                            cycle_detected = True
                            cycle_start_time = elapsed_time
                        elif cycle_detected and force < threshold:
                            cycle_status = "Cycle Ends"
                            cycle_detected = False
                            if cycle_start_time is not None:
                                cycle_duration = elapsed_time - cycle_start_time
                                # print('cycle_duration', cycle_duration)
                                cycle_times.append(cycle_duration)
                            
                        frame = create_base_frame(screen_width, screen_height, inner_frame_size, frame_margin_x, frame_margin_y, image=current_image)
                        frame = overlay_text(frame, "Detecting Cycle...", (frame_margin_x + 20, frame_margin_y - 30))
                        frame = overlay_text(frame, f"{cycle_status}", (frame_margin_x + 20, frame_margin_y + inner_frame_size + 50))
                        cv2.imshow(window_name, frame)
                        
                        if elapsed_time > initialization_time:
                            avg_cycle_time = np.mean(cycle_times) if cycle_times else 4.0
                            recommended_cycle_time = avg_cycle_time * 1.1
                            measuring_level = False
                            showing_recommended = True
                            showing_recommended_start = time.time()
                            print(f"Cycle detection complete. Recommended cycle time: {recommended_cycle_time:.2f} seconds")
                            
                    elif showing_recommended:
                        elapsed_time = time.time() - showing_recommended_start
                        frame = create_base_frame(screen_width, screen_height, inner_frame_size, frame_margin_x, frame_margin_y, image=cv2.imread('./content/head/1.jpg'))
                        frame = overlay_text(frame, f"Recommended Cycle Time: {recommended_cycle_time:.2f}s", (frame_margin_x + 20, frame_margin_y + inner_frame_size + 50))
                        frame = overlay_text(frame, "'Enter' to accept or 'S' to set manually.",  (frame_margin_x + 20, frame_margin_y -30))
                        cv2.imshow(window_name, frame)
                        
                        key = cv2.waitKey(1) & 0xFF
                        if key == 13:
                            showing_recommended = False
                            start_time = time.time()
                        elif key == ord('s'):
                            manual_input = input("Enter the cycle time manually (in seconds): ").strip()
                            recommended_cycle_time = float(manual_input)
                            showing_recommended = False
                            start_time = time.time()
                        
                    else:
                        elapsed_time = time.time() - start_time
                        # print(elapsed_time)
                        section_duration = recommended_cycle_time * 4
                        current_section = folders[int(elapsed_time // section_duration) % len(folders)]
                        images = section_images[current_section]

                        # force 값 정규화
                        normalized_force = np.clip(
                            (force - force_min) / (force_max - force_min) * (len(images) - 1) , 0, len(images) - 1
                        )
                        level = int(normalized_force)

                        

                        current_image = images[level]
                        frame = create_base_frame(screen_width, screen_height, inner_frame_size, frame_margin_x, frame_margin_y, image=current_image)
                        
                        
                        # Red dot을 inner_frame에 그리기
                        x, y = get_dot_position((frame_margin_x, frame_margin_y), inner_frame_size, elapsed_time, recommended_cycle_time)
                        cv2.circle(frame, (x, y), 20, (0, 150, 0), -1)
                        
                        # 각 사각형 변의 중심 좌표 계산
                        top_center = (frame_margin_x + inner_frame_size // 2 - 10, frame_margin_y - 30)  # 상단
                        right_center = (frame_margin_x + inner_frame_size + 20, frame_margin_y + inner_frame_size // 2)  # 오른쪽
                        bottom_center = (frame_margin_x + inner_frame_size // 2 - 11, frame_margin_y + inner_frame_size + 50)  # 하단
                        left_center = (frame_margin_x - 70, frame_margin_y + inner_frame_size // 2)  # 왼쪽
                        cv2.putText(frame, "In", top_center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.putText(frame, "Out", right_center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.putText(frame, "In", bottom_center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.putText(frame, "Out", left_center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

                        # 결과 출력
                        cv2.imshow(window_name, frame)
                else:
                    print("No sensor values available.")
            else:
                print("Failed to read from device.")
                
            # Break on ESC key
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break

    except KeyboardInterrupt:
        print("Animation interrupted.")

    finally:
        device.stop()
        device.close()
        godirect.quit()
        cv2.destroyAllWindows()
        print("GoDirect device closed.")