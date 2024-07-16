from database import get_database_connection

# 连接数据库
db = get_database_connection()
cursor = db.cursor()

# 查询歌单信息
while True:
    print('程序操作 playlists 表以及 playlist_songs 表 批量插入有序的歌曲id')
    playlistId = int(input("请输入要修改的歌单id (输入0退出)："))

    if playlistId == 0:
        print("程序已退出")
        break

    cursor.execute(f"SELECT * FROM playlists WHERE PlaylistID = {playlistId}")
    playlist = cursor.fetchone()

    if playlist:
        print("歌单信息：")
        print(playlist)

        # 获取用户输入的起始值和结束值
        start_value = int(input("请输入起始值（正整数）："))
        end_value = int(input("请输入结束值（正整数）："))

        # 检查用户输入的值
        if start_value <= 0 or end_value <= 0 or start_value > end_value:
            print("请输入合法的起始值和结束值（均为正整数且起始值应小于等于结束值）")
        else:
            # 构建 SQL 插入语句
            sql = "INSERT INTO playlist_songs (PlaylistID, SongID) VALUES"
            values = []
            for i in range(start_value, end_value + 1):
                values.append(f"({playlistId}, {i})")

            sql += ",\n".join(values)

            # 执行 SQL 插入操作
            cursor.execute(sql)

            # 提交更改
            db.commit()

            print(f"成功插入数据，从 {start_value} 到 {end_value}")
    else:
        print(f"歌单ID为 {playlistId} 的歌单不存在，将为您创建该歌单项")

        # 创建新歌单项并为UserID提供默认值
        name = input("请输入歌单名称：")
        description = input("请输入歌单描述：")

        # 创建新歌单项并为UserID提供默认值
        cursor.execute(
            f"INSERT INTO playlists (PlaylistID, UserID, Name, Description) VALUES ({playlistId}, 1, '{name}', '{description}')")
        db.commit()
        print(f"已成功创建歌单项：{playlistId}")

# 关闭数据库连接
cursor.close()
db.close()
