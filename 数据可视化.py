# -*- coding: utf-8 -*-
import socket
from threading import Thread
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np


def calculate_dew_point(temperature, humidity):
    """计算露点温度"""
    a = 17.27
    b = 238.3
    alpha = ((a * temperature) / (b + temperature)) + np.log(humidity / 100.0)
    return (b * alpha) / (a - alpha)


def show_temphum_by_day(day=None, device=""):
    """
    显示某天24小时的温度、湿度和露点温度折线图

    参数:
    day (str): 日期，格式为"YYYY-MM-DD"，默认为昨天
    device (str): 设备名称
    """
    if day is None:
        # 默认使用昨天的日期
        day = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host='xxx',
            database='xxx',
            user='xxx',
            password='xxx',
            port=xxxx
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # 执行查询 - 获取指定日期的所有数据
            query = """
                SELECT create_at, temperature, humidity 
                FROM tb_temphum 
                WHERE device = %s 
                  AND DATE(create_at) = %s 
                ORDER BY create_at ASC
            """
            cursor.execute(query, (device, day))
            results = cursor.fetchall()

            if not results:
                print(f"未找到{day}的记录")
                return

            # 初始化24小时数据数组
            hours = list(range(24))
            hourly_temp = [None] * 24
            hourly_humidity = [None] * 24
            hourly_dew_point = [None] * 24
            count_per_hour = [0] * 24

            # 按小时分组计算平均值
            for row in results:
                dt = row[0]
                hour = dt.hour
                temp = row[1]
                humidity = row[2]

                if hourly_temp[hour] is None:
                    hourly_temp[hour] = temp
                    hourly_humidity[hour] = humidity
                else:
                    # 计算平均值
                    hourly_temp[hour] = (hourly_temp[hour] * count_per_hour[hour] + temp) / (count_per_hour[hour] + 1)
                    hourly_humidity[hour] = (hourly_humidity[hour] * count_per_hour[hour] + humidity) / (
                                count_per_hour[hour] + 1)

                count_per_hour[hour] += 1

            # 计算露点温度
            for h in range(24):
                if hourly_temp[h] is not None and hourly_humidity[h] is not None:
                    hourly_dew_point[h] = calculate_dew_point(hourly_temp[h], hourly_humidity[h])

            # 绘制图表
            fig, ax1 = plt.subplots(figsize=(14, 7))

            # 温度和露点温度使用左侧Y轴
            color = 'tab:red'
            ax1.set_xlabel('时间 (小时)')
            ax1.set_ylabel('温度 (°C)', color=color)
            line1, = ax1.plot(hours, hourly_temp, marker='o', linestyle='-', color=color, label='温度')
            line3, = ax1.plot(hours, hourly_dew_point, marker='s', linestyle='--', color='tab:purple', label='露点温度')
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.set_ylim(15, 40)

            # 湿度使用右侧Y轴
            ax2 = ax1.twinx()
            color = 'tab:blue'
            ax2.set_ylabel('相对湿度 (%)', color=color)
            line2, = ax2.plot(hours, hourly_humidity, marker='^', linestyle='-', color=color, label='湿度')
            ax2.tick_params(axis='y', labelcolor=color)
            ax2.set_ylim(30, 100)

            # 设置X轴为0-23小时
            plt.xticks(hours)
            plt.title(f'{day} 温度、湿度和露点温度变化')

            # 添加图例
            lines = [line1, line2, line3]
            labels = [line.get_label() for line in lines]
            ax1.legend(lines, labels, loc='upper left')

            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.show()

    except Error as e:
        print(f"数据库错误: {e}")
    finally:
        # 关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")


if __name__ == "__main__":
    # 示例：显示昨天的温湿度数据
    show_temphum_by_day()

    # 或者指定日期和设备
    # show_temphum_by_day("2025-07-09", "device1")
