Python 3.9.9 (tags/v3.9.9:ccb0e6a, Nov 15 2021, 18:08:50) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> #导入相关模块
import socket
#import requests
from threading import Thread
import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime
from threading import Lock

# 边缘节点TCP服务器配置
HOST = 'XXXX'  # 监听所有网络接口
PORT = XXXX    # 监听端口

#预处理数据
def process_data(data):
    devid,temp, hum = data.split(',')
    temp = float(temp)
    hum = float(hum)
    # 示例：如果数据异常，则返回None
    if temp < -40 or temp > 100 or hum < 0 or hum > 100:
        return None
    return (devid,temp, hum)
 
#处理客户端连接   
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        data = conn.recv(1024).decode('utf-8').strip()
        print(f"Received data: {data}")
        # 数据处理
        try:
            processed = process_data(data)
            if processed is None:
                print("Invalid data, discarded.")
                return
            devid,temp, hum = processed
            
            # 示例：插入单条模拟数据
            insert_temphum_data(
              device_id=devid,
              temperature=temp,
              humidity=hum
    )
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            return

#将数据插入数据库
def insert_temphum_data(device_id, temperature, humidity):
    try:
        #连接数据库
        connection = mysql.connector.connect(
            host='XXXX',
            database='XXXX',
            user='XXXX',
            password='XXXX',
            port=XXXX
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            #插入数据的SQL查询
            sql = """
            INSERT INTO tb_temphum (device, temp, hum) 
            VALUES (%s, %s, %s)
            """
            values = (device_id, temperature, humidity)
            
            #执行插入
            cursor.execute(sql, values)
            connection.commit()
            
            print(f"成功插入记录: 设备={device_id}, 温度={temperature}, 湿度={humidity}")
            print(f"插入ID: {cursor.lastrowid}")  #获取自动生成的ID
            
    except Error as e:
        print(f"数据库错误: {e}")
        
    finally:
        #关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")
            

#运行服务器
def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Edge server listening on {HOST}:{PORT}")
        id = 1
        while True:
            conn, addr = s.accept()
            # 每个客户端连接使用独立的线程处理
            print(f"第{id}条数据")
            id+=1
            Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    run_server()