import serial
import pyautogui
import time

# 禁用PyAutoGUI的安全特性
pyautogui.FAILSAFE = False

# 串口设置
ser = serial.Serial('COM15', baudrate=115200, timeout=1)  # COM6为你的串口号(需要在设备管理器中查看端口)

try:
    # 获取屏幕大小
    screen_width, screen_height = pyautogui.size()

    # 初始化计数器和清空缓冲区的时间间隔
    count = 0
    clear_buffer_interval = 10  # 每隔10次循环清空一次缓冲区
    
    # 记录上次接收到数据的时间
    last_data_time = time.time()

    while True:
        # 读取串口数据
        data = ser.read(10)  # 读取最多10个字节的数据
        


        # 清空串口接收缓冲区
        count += 1
        if count >= clear_buffer_interval:
            ser.flushInput()  # 清空串口接收缓冲区
            count = 0  # 重置计数器

        # 查找包头和包尾
        header_index = data.find(b'\x02')
        footer_index = data.find(b'\x03')

        if header_index != -1 and footer_index != -1:
            # 更新上次接收到数据的时间
            last_data_time = time.time()
            # 提取有效数据
            valid_data = data[header_index + 1:footer_index]

            # 解析数据
            if len(valid_data) >= 4:  # 检查有效数据长度是否足够
                # 从有效数据中分别提取两个16位数据
                data1 = int.from_bytes(valid_data[:2], byteorder='little')
                data2 = int.from_bytes(valid_data[2:4], byteorder='little')

                # 映射数据到鼠标坐标
                x = int(screen_width * data1 / 555)
                y = int(screen_height * data2 / 430)

                # 控制鼠标移动到绝对位置
                pyautogui.moveTo(x, y)

                print('\rX:', data1, 'Y:', data2, end='')  # 输出坐标值
        print(1)
        # 如果超过10秒没有接收到数据，则退出循环
        if time.time() - last_data_time > 5:
            
            break

finally:
    # 关闭串口连接
    ser.close()
