# connect_database.py
import pymysql

# 資料庫參數設定
connection_params = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "kevinbear60404",
    "db": "meeting room",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

'''
m_id = "B1044127"  # 確保 m_id 是字符串
try:
    # 建立資料庫連接
    with pymysql.connect(**connection_params) as connection:
        with connection.cursor() as cursor:
            m_id_query = "SELECT r_no, r_start, r_end, room_no FROM reserve WHERE c_id = %s ORDER BY r_no ASC"
            cursor.execute(m_id_query, (m_id,))  # 不需要轉換為字符串，直接使用
            results = cursor.fetchall()
            print(results)  # 打印查詢結果
except pymysql.MySQLError as e:
    print(f"資料庫錯誤: {e}")
'''

try:
    with pymysql.connect(**connection_params) as connection:
        with connection.cursor() as cursor: 
            r_no = 7
            sql = "DELETE FROM reserve WHERE r_no = %s"
            cursor.execute(sql, (r_no,))
        connection.commit()  # 确保提交事务
except pymysql.MySQLError as e:
    print("資料庫連接錯誤，無法查詢預約資料")

  
        
with pymysql.connect(**connection_params) as connection:
        with connection.cursor() as cursor:
            m_id = "B1044127"
            m_id_query = "SELECT r_no, r_start, r_end, room_no FROM reserve WHERE c_id = %s ORDER BY r_no ASC"
            cursor.execute(m_id_query, (m_id,))
            results = cursor.fetchall()
        print(results)
