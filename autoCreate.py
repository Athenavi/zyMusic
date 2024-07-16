import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from datetime import datetime
from database import get_database_connection

# 连接数据库
db = get_database_connection()
cursor = db.cursor()


def add_song_to_database(file_path):
    # 从文件名中提取歌手和歌曲名
    file_name = os.path.basename(file_path)
    artist, title = file_name.split(" - ")[0], file_name.split(" - ")[1].replace(".mp3", "")

    # 使用 mutagen 获取音乐文件的详细信息
    audio = MP3(file_path, ID3=ID3)
    genre = audio.get("TCON").text[0] if audio.get("TCON") else "Unknown Genre"
    duration = int(audio.info.length)
    album = audio.get("TALB").text[0] if audio.get("TALB") else "Unknown Album"

    # 询问用户填写其他信息
    release_date = input(f"请输入歌曲 {title} 的发布日期（YYYY-MM-DD，直接回车使用默认日期 1980-01-01）：")
    if release_date == "":
        release_date = "1980-01-01"
    else:
        while True:
            try:
                datetime.strptime(release_date, '%Y-%m-%d')
                break
            except ValueError:
                print("日期格式错误，请按照 YYYY-MM-DD 的格式输入日期。")
                release_date = input(f"请输入歌曲 {title} 的发布日期（YYYY-MM-DD，直接回车使用默认日期 1980-01-01）：")

    file_path = file_path
    cover_image_path = input(f"请输入歌曲 {title} 的封面图片路径：")
    lyrics = input(f"请输入歌曲 {title} 的歌词：")
    language = input(f"请输入歌曲 {title} 的语言（直接回车使用默认语言 '国语'）：")
    if language == "":
        language = "国语"

    # 查询歌手是否已存在，如果不存在则插入新记录
    cursor.execute("SELECT ArtistID FROM artists WHERE Name = %s", (artist,))
    result = cursor.fetchone()
    if result:
        artist_id = result[0]
    else:
        cursor.execute("INSERT INTO artists (Name) VALUES (%s)", (artist,))
        artist_id = cursor.lastrowid

    # 查询专辑是否已存在，如果不存在则插入新记录
    cursor.execute("SELECT AlbumID FROM albums WHERE Title = %s", (album,))
    result = cursor.fetchone()
    if result:
        album_id = result[0]
    else:
        cursor.execute("INSERT INTO albums (Title, ArtistID) VALUES (%s, %s)", (album, artist_id))
        album_id = cursor.lastrowid

    # 将歌曲信息插入数据库
    cursor.execute(
        "INSERT INTO songs (Title, ArtistID, AlbumID, Genre, Duration, ReleaseDate, FilePath, CoverImagePath, Lyrics, "
        "Language) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (title, artist_id, album_id, genre, duration, release_date, file_path, cover_image_path, lyrics, language))

    db.commit()


def scan_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                add_song_to_database(file_path)


# 包含歌曲的文件夹路径
folder_path = input(f"请输入歌曲所在位置文件夹地址")
scan_folder(folder_path)

# 关闭数据库连接
db.close()
