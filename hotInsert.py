import mysql

from database import get_database_connection

# 连接数据库
db = get_database_connection()
cursor = db.cursor()


def check_existing_data(target_id, type):
    query = f"SELECT * FROM hot WHERE TargetID = {target_id} AND Type = '{type}'"
    cursor.execute(query)
    result = cursor.fetchone()
    return result


def insert_data(target_id, type, position, update_time):
    sql = f"INSERT INTO hot (TargetID, Type, Position, UpdateTime) VALUES ({target_id}, '{type}', {position}, '{update_time}')"
    try:
        cursor.execute(sql)
        db.commit()
        print(f"成功插入数据：TargetID={target_id}, Type={type}")
    except mysql.connector.Error as err:
        print(f"插入数据失败：{err}")
        handle_duplicate_key_error(target_id, type)


def get_record_by_id(id):
    try:
        cursor = db.cursor()
        query = "SELECT * FROM hot WHERE TargetID = %s;"
        cursor.execute(query, (id,))
        repeat_line = cursor.fetchone()
        print(repeat_line)
        return repeat_line
    except mysql.connector.Error as err:
        print(f"插入数据失败：{err}")
        handle_duplicate_key_error(id, type)
        return '出错了'
    finally:
        cursor.close()


def handle_duplicate_key_error(target_id, type):
    print(f"遇到重复键错误：TargetID={target_id}, Type={type}")
    choice = input("请选择操作：0-结束程序，1-修改并继续，2-不创建跳出本次循环：")
    if choice == '0':
        exit()
    elif choice == '1':
        print("请修改以下记录：")
        record = get_record_by_id(target_id)
        print(record)
        pass
        # 完成修改后继续
        handle_duplicate_key_error(target_id, type)
    elif choice == '2':
        return


def check_hot_Max_targetID():
    try:
        print("程序操作 hot 表批量插入有序的歌曲信息")
        cursor = db.cursor()
        cursor.execute("SELECT MAX(targetID) AS max_targetID FROM hot;")
        print("当前TargetID最大值:" + str(cursor.fetchone()))
        pass
    except mysql.connector.Error as err:
        print(f"插入数据失败：{err}")
        handle_duplicate_key_error(id, type)
        return '出错了'
    finally:
        cursor.close()


check_hot_Max_targetID()
start_value = int(input("请输入起始值（正整数）："))
end_value = int(input("请输入结束值（正整数）："))

if start_value <= 0 or end_value <= 0 or start_value > end_value:
    print("请输入合法的起始值和结束值（均为正整数且起始值应小于等于结束值）")
else:
    for i in range(start_value, end_value + 1):
        existing_data = check_existing_data(i, 'SONG')
        if existing_data:
            print(f"已存在数据：TargetID={i}, Type=SONG")
            choice = input("请选择操作：0-结束程序，1-继续，2-不创建跳出本次循环：")
            if choice == '0':
                exit()
            elif choice == '1':
                insert_data(i, 'SONG', i, '2024-07-08 08:00:00')
            elif choice == '2':
                continue
        else:
            insert_data(i, 'SONG', i, '2024-07-08 08:00:00')

# 关闭数据库连接
cursor.close()
db.close()
