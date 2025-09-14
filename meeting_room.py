#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
import time
import mysql.connector
from mfrc522 import SimpleMFRC522
from waveshare_epd import epd7in5b_V2
import datetime
import threading
import schedule
import logging
from PIL import Image,ImageDraw,ImageFont
import traceback
import RPi.GPIO as GPIO

# 設置 GPIO 模式
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 初始化 RFID 讀卡器
reader = SimpleMFRC522()

room_no = "A001"

# 變數用於保存上次查詢結果
last_reservation_status = None
last_r_no = 0

# 設置 log level
logging.basicConfig()
logger = logging.getLogger('mysql.connector')
logger.setLevel(logging.WARNING)

epd = epd7in5b_V2.EPD()

Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
font60 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
draw_Himage = ImageDraw.Draw(Himage)
draw_other = ImageDraw.Draw(Other)

# 建立 MySQL 資料庫連線
def get_database_connection():
    print("connecting SQL server...")
    return mysql.connector.connect(
        host="192.168.137.1",
        user="rootpro",
        password="root",
        database="meeting_room"
    )

# 更新顯示內容
def epaper_change(reservation_status, room_no=None, r_no=None):
    global last_reservation_status
    global Himage
    global Other
    global font60
    global draw_Himage
    global draw_other
    
    # 初始化電子紙
    logging.info("epd7in5b_V2 Demo")
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    print("epaper already")

    if reservation_status == "empty":
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        font60 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
        draw_Himage = ImageDraw.Draw(Himage)
        draw_other = ImageDraw.Draw(Other)
        draw_Himage.text((325, 00), '空室', font=font60, fill=0)  # 需替換成實際的顯示內容
        epd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
        print("change to empty")
    elif reservation_status == "reserved":
        # TODO: 更新電子紙顯示內容，使用 room_no 和 r_no
        # 可以使用 room_no 和 r_no 進行顯示內容的設定
        # 使用 r_no 查詢 topic 和 customer 資料
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        font60 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
        draw_Himage = ImageDraw.Draw(Himage)
        draw_other = ImageDraw.Draw(Other)
        topic, c_name = get_reservation_info(r_no)
        print(f"預約主題: {topic}, 預約者: {c_name}")
        draw_Himage.text((50, 300), f'主题: {topic}', font=font60, fill=0)
        draw_Himage.text((50, 200), f'借用人:{c_name}', font=font60, fill=0)
        draw_Himage.text((300, 100), '未簽到', font=font60, fill=0)
        epd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
        print("change to reserved")
    elif reservation_status == "in_use":
        # TODO: 更新電子紙顯示內容，使用 room_no 和 r_no
        # 可以使用 room_no 和 r_no 進行顯示內容的設定
        # 使用 r_no 查詢 topic 和 customer 資料
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        font60 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
        draw_Himage = ImageDraw.Draw(Himage)
        draw_other = ImageDraw.Draw(Other)
        topic, c_name = get_reservation_info(r_no)
        print(f"預約主題: {topic}, 預約者: {c_name}")
        draw_Himage.text((50, 300), f'主题: {topic}', font=font60, fill=0)
        draw_Himage.text((50, 200), f'借用人:{c_name}', font=font60, fill=0)
        draw_Himage.text((300, 100), '使用中', font=font60, fill=0)
        epd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
        print("change to in used")

    last_reservation_status = reservation_status

# 查詢預約時段
def query_reservation_status(room_no):
    global last_reservation_status
    global last_r_no
    print("looking for reserved")

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = "SELECT * FROM reserve WHERE room_no = %s AND r_start <= %s AND r_end >= %s"
    
    with get_database_connection() as conn, conn.cursor() as cursor:
        cursor.execute(query, (room_no, current_time, current_time))
        reservations = cursor.fetchall()
        print("get reservations")

        if reservations:
            r_no = reservations[0][0]  # 假設 r_no 是預約編號的欄位名稱
            r_start = reservations[0][1]
            # (5.) 若上次查詢的結果是有預約時段，則變更電子紙為顯示"預約空室"
            if last_reservation_status == "empty":
                last_r_no = r_no
                epaper_change("reserved", room_no, r_no)
            if last_reservation_status == "reserved" and last_r_no != r_no:
                last_r_no = r_no
                epaper_change("reserved", room_no, r_no)
            if last_reservation_status == "in_use" and last_r_no != r_no:
                last_r_no = r_no
                epaper_change("reserved", room_no, r_no)
                
            print("last_reservation_status complete")

            # (3.) 若當前時間距離預約開始時間已經過了十分鐘，且該預約時段的簽到記錄(s_in)為空值，則將該筆預約資料的r_del欄位改為1。
            ten_minutes_later = (r_start + datetime.timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
                                 
            cursor.execute("SELECT s_in FROM sign WHERE s_no = %s", (r_no,))
            signin = cursor.fetchone()
                                 
            if signin[0] is None:
                if current_time > ten_minutes_later:
                    cursor.execute("UPDATE reserve SET r_del = 1 WHERE r_no = %s", (r_no,))
                    conn.commit()
                    print(f"預約 {r_no} 已標記為過期")
                
            print("ten min over")

            # (4.) 若查詢到這間會議室的當前時間有不只一筆預約資料，則找出r_del為1的預約資料，
            # 並將該筆資料的預約結束時間更改為另一筆預約資料的預約開始時間，以用來達到同一間會議室的預約時段不重複的原則。
            if len(reservations) > 1:
                for i in range(1, len(reservations)):
                    if reservations[i][7] == 1:
                        cursor.execute("UPDATE reserve SET r_end = %s WHERE r_no = %s", (reservations[i][4], r_no))
                        conn.commit()
                        print(f"預約 {r_no} 的結束時間已更新")
            
        else:
            if last_reservation_status == "reserved":
                last_reservation_status == "empty"
                epaper_change("empty", room_no, 1)
            if last_reservation_status == "in_use":
                last_reservation_status == "empty"
                epaper_change("empty", room_no, 1)

# 獲取預約信息
def get_reservation_info(r_no):
    print("getting topic and c_name...")
    query = "SELECT topic, c_id FROM reserve WHERE r_no = %s"

    with get_database_connection() as conn, conn.cursor() as cursor:
        cursor.execute(query, (r_no,))
        result = cursor.fetchone()

        if result:
            topic, c_id = result
            # 使用 c_id 查詢 customer 資料
            c_name = get_customer_name(c_id)
            return topic, c_name

    return None, None

# 獲取顧客名稱
def get_customer_name(c_id):
    print("getting c_id")
    query = "SELECT c_name FROM customer WHERE c_id = %s"

    with get_database_connection() as conn, conn.cursor() as cursor:
        cursor.execute(query, (c_id,))
        result = cursor.fetchone()

        if result:
            return result[0]

    return None

# 處理 RFID 卡片
def handle_rfid_card():
    global last_r_no
    while True:
        try:
            print("請將卡片靠近讀卡器...")
            id, text = reader.read()
    
            # 連接到 MySQL 資料庫
            conn = get_database_connection()
            cursor = conn.cursor()
            print("server connected")
    
            # 查詢卡片ID是否存在於資料庫
            cursor.execute("SELECT c_id FROM customer WHERE c_uid = %s", (str(id),))
            result = cursor.fetchone()
            print("looking ID complete")
            print(result)
    
            if result:
                c_id = result[0]
            else:
                # 卡片ID不存在於資料庫中
                print("無效的卡片")
    
            if result:
                # 卡片ID存在於資料庫中
                # 獲取當前時間
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                print("have time")
    
                # 查詢當前預約情況，同時檢查會議室編號
                cursor.execute(
                    "SELECT * FROM reserve WHERE room_no = %s AND r_start <= %s AND r_end >= %s", (room_no, current_time, current_time))
                result = cursor.fetchall()
                print("looking for reserve now")
    
                if result:
                    reservation = result[0]  # 假設只查詢第一個結果
                    r_no = reservation[0]
                    user_id = reservation[3]
                    print(user_id)
    
                    # 檢查是否在同一間會議室並且同一個預約者
                    if user_id == c_id:
                        print("user id = c id")
                        # 檢查是否已經有簽到記錄
                        cursor.execute(
                            "SELECT * FROM sign WHERE c_id = %s AND room_no = %s AND s_in <= %s AND s_out IS NULL",
                            (user_id, room_no, current_time))
                        existing_sign = cursor.fetchone()
                        print("looking for sign")
    
                        if existing_sign:
                            print("have sign")
                            # 如果已經有簽到記錄，update s_out
                            s_no = existing_sign[0]
                            s_in = existing_sign[1]
                            s_out = existing_sign[2]
    
                            # 檢查兩次感應之間是否已經超過 20 sec
                            last_scan_time = time.strptime(str(s_in), '%Y-%m-%d %H:%M:%S')
                            current_time = time.strptime(str(current_time), '%Y-%m-%d %H:%M:%S')
                            time_diff = time.mktime(current_time) - time.mktime(last_scan_time)
    
                            if time_diff >= 20:
                                # 超過 20 sec，進行簽出操作
                                cursor.execute("UPDATE sign SET s_out = %s WHERE s_no = %s", (current_time, s_no))
                                cursor.execute(
                                    "UPDATE reserve SET r_end = %s WHERE room_no = %s AND r_start <= %s AND r_end >= %s",
                                    (current_time, room_no, current_time, current_time))
                                conn.commit()
                                print("簽出成功")
    
                                # 觸發更新顯示
                                last_r_no = r_no
                                last_reservation_status == "empty"
                                epaper_change("empty", room_no, r_no)
                            else:
                                message = f"感應時間間隔太短，還有 {20 - time_diff} 秒"
                                print(message)
    
                        else:
                            print("have no sign")
                            # 沒有簽到記錄，進行簽到操作
                            cursor.execute("UPDATE sign SET s_in = %s WHERE s_no = %s", (current_time, r_no))
                            conn.commit()
                            print("簽到成功")
    
                            # 觸發更新顯示
                            last_r_no = r_no
                            last_reservation_status == "in_use"
                            epaper_change("in_use", room_no, r_no)
                    else:
                        # 卡片id不符合預約者卡片id
                        print("您不是預約者")
    
                else:
                    # 現在不是預約的時間
                    print("現在不是預約的時間")
                    
            # 關閉資料庫連接
            cursor.close()
            conn.close()
                    
        except Exception as e:
            print(f"錯誤：{e}")
            
        except IOError as e:
            logging.info(e)
    
        except KeyboardInterrupt:    
            logging.info("ctrl + c:")
            epd7in5b_V2.epdconfig.module_exit()
            exit()

# 定義執行感應卡片操作的函數
def read_card():
    while True:
        handle_rfid_card()
        time.sleep(1)

# 使用 schedule 定期查詢預約時段
def scheduled_task():
    query_reservation_status(room_no)
    
epaper_change("empty", room_no, 1)

# 啟動感應卡片執行緒
card_thread = threading.Thread(target=read_card)
card_thread.start()

# 每分鐘執行一次定期任務
schedule.every(1).minutes.do(scheduled_task)

# 主程式
while True:
    schedule.run_pending()
    time.sleep(1)
