# %%

from gdx import gdx
gdx = gdx.gdx()

gdx.open(connection='usb')
gdx.select_sensors()
gdx.start()

# 활성화된 센서 정보 직접 추출
enabled_sensors = gdx.enabled_sensors
if enabled_sensors:
    column_headers = []
    for device_sensors in enabled_sensors:
        for sensor in device_sensors:
            # 센서 설명과 단위를 수동으로 조합
            sensor_info = f"{sensor.sensor_description} ({sensor.sensor_units})"
            column_headers.append(sensor_info)
    print("\nColumn Headers:")
    print("\n".join(column_headers))
else:
    print("No sensors enabled.")

# 데이터 읽기 및 출력
for i in range(5):
    measurements = gdx.read()
    if measurements is None:
        break
    print(measurements)

gdx.stop()
gdx.close()

# %%
import time
from gdx import gdx

# GDX 객체 초기화
gdx = gdx.gdx()

# 장치 연결 및 센서 선택
gdx.open(connection='usb')
gdx.select_sensors()
gdx.start()

# 활성화된 센서 정보 직접 추출
enabled_sensors = gdx.enabled_sensors
if enabled_sensors:
    column_headers = []
    for device_sensors in enabled_sensors:
        for sensor in device_sensors:
            # 센서 설명과 단위를 수동으로 조합
            sensor_info = f"{sensor.sensor_description} ({sensor.sensor_units})"
            column_headers.append(sensor_info)
    print("\nColumn Headers:")
    print("\n".join(column_headers))
else:
    print("No sensors enabled.")

# 데이터 읽기 및 30초 동안 수집
print("\nCollecting data for 30 seconds...\n")
start_time = time.time()  # 시작 시간 기록

while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time > 30:  # 30초가 지나면 루프 종료
        break

    measurements = gdx.read()
    if measurements is None:
        break
    print(measurements)

# 종료
gdx.stop()
gdx.close()

print("\nData collection complete.")

# %%
import time
from gdx import gdx

# GDX 객체 초기화
gdx = gdx.gdx()

# 장치 연결 및 센서 선택
gdx.open(connection='usb')

# 센서 선택
print("\nList of sensors for GDX-RB")
print("1: Force (N)")
print("2: Respiration Rate (bpm)")
print("4: Steps (steps)")
print("5: Step Rate (spm)")
sensor_selection = input("Enter sensor numbers separated by commas (e.g., 1,2): ")
gdx.select_sensors([int(s.strip()) for s in sensor_selection.split(",")])

# 샘플링 주기 설정
sampling_period = int(input("Enter the sampling period (milliseconds): "))
gdx.start(period=sampling_period)

# 활성화된 센서 확인
enabled_sensors = gdx.enabled_sensors
if enabled_sensors:
    column_headers = []
    for device_sensors in enabled_sensors:
        for sensor in device_sensors:
            sensor_info = f"{sensor.sensor_description} ({sensor.sensor_units})"
            column_headers.append(sensor_info)
    print("\nColumn Headers:")
    print("\n".join(column_headers))
else:
    print("No sensors enabled.")

# 데이터 읽기 및 30초 동안 수집
print("\nCollecting data for 30 seconds...\n")
start_time = time.time()  # 시작 시간 기록

while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time > 30:  # 30초가 지나면 루프 종료
        break

    measurements = gdx.read()
    if measurements is None:
        print("No data to return.")
        break
    print(measurements)

# 종료
gdx.stop()
gdx.close()

print("\nData collection complete.")

# %%
