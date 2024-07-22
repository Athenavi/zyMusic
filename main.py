import logging
import os
import uuid
from datetime import timedelta
from io import BytesIO

import bcrypt
from PIL import Image
from flask import Flask, jsonify, request, send_file, abort, make_response, session
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity,
)
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3

from database import test_database_connection, get_database_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=3)
CORS(app)

# 配置JWT
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

base_dir = os.path.dirname(os.path.abspath(__file__))
print(base_dir)

logging.basicConfig(filename='user.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

domain = "http://127.0.0.1/"


@app.route('/api/count_users', methods=['POST'])
def count_users():
    # 获取请求体中的数据
    data = request.json
    user_ip = data.get('userIP')
    user_agent = data.get('userAgent')

    # 记录用户信息到日志文件
    logging.info(f"User IP: {user_ip}, User Agent: {user_agent}")

    # 返回一个响应
    return jsonify({"message": "User data received", "userIP": user_ip}), 200


def validate_password(password_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


@app.route('/login', methods=['POST'])
def login():
    username = request.args.get('username')
    password = request.args.get('pwd')

    if username is None or password is None:
        return jsonify({"msg": "Missing username or password"}), 400

    db = get_database_connection()
    cursor = db.cursor()

    try:
        query = "SELECT UserID, Username, Password FROM users WHERE Username = %s;"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({"msg": "Bad username or password"}), 401

        if validate_password(result[2], password):
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=120)  # 2 hours
            session['user_id'] = result[0]
            access_token = create_access_token(identity=result[0])
            return jsonify({"access_token": access_token}), 200
        else:
            return jsonify({"msg": "Bad username or password"}), 401

    except Exception as e:
        return jsonify({"msg": str(e)}), 500

    finally:
        cursor.close()
        db.close()


@app.route('/protected')
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """ 刷新JWT token的路由 """
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_access_token}), 200


@app.route('/')
def home():
    """ 默认路由，不需要认证 """
    return jsonify({"message": "service is running "})


@app.route('/login/cellphone', methods=['GET'])
def login_cellphone():
    phone = request.args.get('phone')
    password = request.args.get('password')
    md5_password = request.args.get('md5_password')
    captcha = request.args.get('captcha')
    countrycode = request.args.get('countrycode', '86')
    # 这里你应该添加登录处理逻辑
    return jsonify({"message": "登录成功", "phone": phone, "countrycode": countrycode})


# 生成登录链接并保存到缓存
def generate_login_url():
    login_key = str(uuid.uuid4())
    # 在这里将登录链接保存到Cache
    return login_key


qr_api_url = "http://api.7trees.cn/qrcode/"


@app.route('/login/qr/key', methods=['GET'])
def login_qr_key():
    # 生成登录链接
    login_key = generate_login_url()

    # 登陆链接
    login_url = domain + "login/callback?key=" + login_key

    return jsonify({"code": "200", "key": login_key, "qr_url": ''})


@app.route('/login/callback', methods=['POST'])
def login_callback():
    # 根据传入的参数获取登录key
    login_key = request.form.get('key')

    # 在这里根据登录key从缓存中获取用户信息，并执行登录逻辑
    # 登录成功后返回相应的响应

    return jsonify({"code": "200", "message": "Login successful"})


@app.route('/login/qr/check', methods=['GET'])
def login_qr_check():
    key = request.args.get('key')
    # 添加检查二维码扫描状态逻辑
    return jsonify({"message": "二维码扫描状态检查", "key": key, "status": "803"})


@app.route('/register/anonimous', methods=['GET'])
def register_anonimous():
    # 添加游客登录逻辑
    return jsonify({"message": "游客登录成功", "cookie": "anonimous_cookie"})


@app.route('/login/refresh', methods=['GET'])
def refresh_login():
    # 此处仅为示例，具体实现需要根据实际需求编写
    return jsonify(message="Login refreshed successfully."), 200


@app.route('/captcha/sent', methods=['GET'])
def send_captcha():
    phone = request.args.get('phone')
    ctcode = request.args.get('ctcode', '86')
    # 具体实现
    return jsonify(message="Captcha sent successfully."), 200


@app.route('/captcha/verify', methods=['GET'])
def verify_captcha():
    phone = request.args.get('phone')
    captcha = request.args.get('captcha')
    ctcode = request.args.get('ctcode', '86')
    # 具体实现
    return jsonify(message="Captcha verified successfully."), 200


@app.route('/register/cellphone', methods=['GET'])
def register():
    # 获取必要参数
    captcha = request.args.get('captcha')
    phone = request.args.get('phone')
    password = request.args.get('password')
    nickname = request.args.get('nickname')
    countrycode = request.args.get('countrycode', '86')
    # 具体实现
    return jsonify(message="Registered successfully."), 200


@app.route('/cellphone/existence/check', methods=['GET'])
def check_phone_existence():
    phone = request.args.get('phone')
    countrycode = request.args.get('countrycode', '86')
    # 具体实现
    return jsonify(existence=True), 200


@app.route('/activate/init/profile', methods=['POST'])
def init_profile():
    nickname = request.args.get('nickname')
    # 具体实现
    return jsonify(message="Profile initialized successfully."), 200


@app.route('/nickname/check', methods=['GET'])
def check_nickname():
    nickname = request.args.get('nickname')
    # 具体实现
    return jsonify(available=True), 200


@app.route('/rebind', methods=['GET'])
def rebind_phone():
    oldcaptcha = request.args.get('oldcaptcha')
    captcha = request.args.get('captcha')
    phone = request.args.get('phone')
    ctcode = request.args.get('ctcode', '86')
    # 具体实现
    return jsonify(message="Phone rebinded successfully."), 200


@app.route('/logout', methods=['GET'])
def logout():
    # 具体实现
    return jsonify(message="Logged out successfully."), 200


@app.route('/login/status', methods=['GET'])
def login_status():
    # 具体实现
    return jsonify(status="Logged in"), 200


@app.route('/api/Recommend', methods=['GET'])
def api_Recommend():
    pageType = request.args.get('pageType')
    db = get_database_connection()
    cursor = db.cursor()

    # 定义一个函数来执行查询并返回结果
    def execute_query(query):
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            if results:
                return results
        except Exception:
            return 'error', 404
        finally:
            cursor.close()
            db.close()

    # 根据不同的 pageType 执行不同的查询
    if pageType == 'al':
        return execute_query("SELECT AlbumID,Title,ReleaseDate FROM albums;")
    elif pageType == 'pl':
        return execute_query("SELECT PlaylistID,Name,Description FROM playlists;")
    else:
        return 'error', 404


@app.route('/api/singer', methods=['GET'])
def api_singer():
    uid = int(request.args.get('uid', 0))

    if uid:
        singer_data = singer_detail(uid)
        if isinstance(singer_data, dict) and singer_data.get('error'):
            return jsonify({'error': 'No singer found'}), 404
        return jsonify({"歌手": singer_data})

    all_singers = get_all_singer()
    if isinstance(all_singers, dict) and all_singers.get('error'):
        return jsonify({'error': 'No singers found'}), 404
    return jsonify({"歌手": all_singers})


def get_all_singer():
    try:
        db = get_database_connection()
        cursor = db.cursor()
        query = "SELECT DISTINCT artists.ArtistID, artists.Name FROM songs INNER JOIN artists ON songs.ArtistID = artists.ArtistID;"
        cursor.execute(query)
        playlists = cursor.fetchall()
        if playlists:
            print(playlists)
            return playlists  # 返回字典对象
        else:
            return {'error': 'No playlists found'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        db.close()


def singer_detail(uid):
    if uid:
        try:
            db = get_database_connection()
            cursor = db.cursor()
            query = "SELECT songs.SongID, songs.Title, artists.Name FROM songs INNER JOIN artists ON songs.ArtistID = artists.ArtistID WHERE artists.ArtistID = {};".format(
                uid)
            print(query)
            cursor.execute(query)
            playlists = cursor.fetchall()
            if playlists:
                return playlists
            else:
                return {'error': 'No playlists found'}
        except Exception as e:
            return {'error': str(e)}
        finally:
            cursor.close()
            db.close()
    else:
        return {'error': '歌手不存在'}


@app.route('/api/Detail', methods=['GET'])
def api_PlayListDetail(pid=0):
    pid = request.args.get('pid')
    pageType = request.args.get('pageType')
    if pid and pageType == 'pl':
        converted_playlist = {"歌曲列表": song_name(pid).json}
        return converted_playlist
    if pid and pageType == 'al':
        converted_playlist = {"歌曲列表": album_detail(pid).json}
        return converted_playlist
    else:
        return 'error', 404


def album_detail(pid):
    if pid:
        try:
            db = get_database_connection()
            cursor = db.cursor()
            query = "SELECT songs.SongID, songs.Title, artists.Name FROM songs INNER JOIN artists ON songs.ArtistID = artists.ArtistID WHERE songs.AlbumID = {};".format(
                pid)
            print(query)
            cursor.execute(query)
            playlists = cursor.fetchall()
            if playlists:
                print(playlists)
                return jsonify(playlists)
            else:
                pass
        except Exception as e:
            pass
        finally:
            cursor.close()
            db.close()
    else:
        return '专辑不存在'


def list_by_uid(uid, list_id):
    if uid and list_id:
        try:
            db = get_database_connection()
            cursor = db.cursor()
            query = "SELECT * FROM `playlists` WHERE UserID={} and PlaylistID={};".format(uid, list_id)
            print(query)
            cursor.execute(query)
            playlists = cursor.fetchall()
            if playlists:
                print(playlists)
                return jsonify(playlists)
            else:
                pass
        except Exception as e:
            pass
        finally:
            cursor.close()
            db.close()
    else:
        pass

    return abort(404, description="暂无推荐")


@app.route('/api/toplist', methods=['GET'])
def api_topLists():
    db = get_database_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT TargetID FROM `hot` WHERE Type='SONG';")
        results = cursor.fetchall()
        hot_id_list = []
        if results:
            for i in results:
                hot_id_list.append(i[0])
            str_list = ','.join(str(x) for x in hot_id_list)
            hot_song_list = song_name_list(str_list)
            return jsonify(hot_song_list)
    except Exception:
        return 'error', 404
    finally:
        cursor.close()
        db.close()


@app.route('/api/album', methods=['GET'])
def api_album():
    db = get_database_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT AlbumID,Title,ReleaseDate FROM albums;")
        results = cursor.fetchall()
        if results:
            return results
    except Exception:
        return 'error', 404
    finally:
        cursor.close()
        db.close()


@app.route('/api/userSongList', methods=['GET'])
def api_userSongList(pid=0):
    pid = request.args.get('pid')
    if pid:
        converted_playlist = {"播放列表": song_name(pid=1).json}
        return converted_playlist
    else:
        return 'error', 404


@app.route('/api/playlistInformation', methods=['GET'])
def get_playlistInformation(pid=0):
    pid = request.args.get('pid')
    if pid:
        try:
            db = get_database_connection()
            cursor = db.cursor()
            query = "SELECT * FROM `playlists` WHERE PlaylistID={};".format(pid)
            print(query)
            cursor.execute(query)
            playlists = cursor.fetchall()
            if playlists:
                print(playlists)
                return playlists
            else:
                pass
        except Exception as e:
            pass
        finally:
            cursor.close()
            db.close()
    else:
        pass
    return abort(404, description="歌单不存在")


@app.route('/api/artistDetail', methods=['GET'])
def api_artistList():
    uid = request.args.get('uid')
    if uid:
        converted_playlist = {"歌曲列表": song_name(uid=uid).json}
        return converted_playlist
    else:
        return 'error', 404


@app.route('/topic/detail/event/hot', methods=['GET'])
def topic_detail_hot_event():
    actid = request.args.get('actid')
    # Implementation placeholder
    return jsonify({'message': 'Topic detail hot events fetched', 'actid': actid})


@app.route('/comment/hotwall/list', methods=['GET'])
def comment_hotwall_list():
    # Implementation placeholder since officially deprecated
    return jsonify({'message': 'Cloud Village Hot Comments currently unavailable'})


@app.route('/playmode/intelligence/list', methods=['GET'])
def playmode_intelligence_list():
    song_id = request.args.get('id')
    pid = request.args.get('pid')
    sid = request.args.get('sid', '')
    # Implementation placeholder
    return jsonify({'message': 'Heartbeat Mode/Intelligent Play list fetched', 'id': song_id, 'pid': pid, 'sid': sid})


@app.route('/event', methods=['GET'])
def get_events():
    pagesize = request.args.get('pagesize', 20)
    lasttime = request.args.get('lasttime', -1)
    # Implementation placeholder
    return jsonify({'message': 'Dynamic messages fetched', 'pagesize': pagesize, 'lasttime': lasttime})


@app.route('/artist/list', methods=['GET'])
def artist_list():
    limit = request.args.get('limit', 30)
    offset = request.args.get('offset', 0)
    initial = request.args.get('initial')
    type = request.args.get('type', -1)
    area = request.args.get('area', -1)
    # Implementation placeholder
    return jsonify(
        {'message': 'Artist list fetched', 'limit': limit, 'offset': offset, 'initial': initial, 'type': type,
         'area': area})


@app.route('/artist/sub', methods=['POST'])
def artist_subscribe():
    artist_id = request.args.get('id')
    t = request.args.get('t')
    # Implementation placeholder
    return jsonify({'message': f'Artist {"subscribed" if t == "1" else "unsubscribed"} successfully', 'id': artist_id})


@app.route('/comment', methods=['POST'])
def comment():
    data = {
        "status": "success",
        "action": request.args.get('t')
    }
    return jsonify(data)


@app.route('/banner')
def banner():
    data = {
        "banners": ["banner1", "banner2"]
    }
    return jsonify(data)


@app.route('/resource/like', methods=['POST'])
def resource_like():
    data = {
        "status": "liked" if request.args.get('t') == '1' else "unliked",
        "id": request.args.get('id')
    }
    return jsonify(data)


@app.route('/playlist/mylike')
def mylike():
    data = {
        "playlists": []
    }
    return jsonify(data)


@app.route('/song')
def song():
    song_id = request.args.get('id')
    if song_id:
        return 'ok'  # 确保这里调用 file() 时传递正确的参数名
    else:
        return "No 'id' provided in query string.", 400


@app.route('/music/<id>.mp3')
def file(id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    musics_dir = os.path.join(base_dir, 'storage')
    music_file_path = os.path.join(musics_dir, id + '.mp3')  # 使用 'id' 作为文件名

    # 检查文件是否存在
    if os.path.exists(music_file_path):
        print(music_file_path)
        print('正在请求的是', id)
        return send_file(music_file_path, mimetype="audio/mp3")
    else:
        db = get_database_connection()
        cursor = db.cursor()
        query = "SELECT FilePath FROM songs WHERE SongID = %s;"
        cursor.execute(query, (id,))
        music_file_path1 = cursor.fetchone()
        if music_file_path1:
            music_file_path1 = music_file_path1[0]  # 提取路径字符串
            if os.path.exists(music_file_path1):
                print(music_file_path1)
                print('正在重新请求的是', id)
                db.close()  # 关闭数据库连接
                return send_file(music_file_path1, mimetype="audio/mp3")
        else:
            print('请求失败', id)
            db.close()  # 关闭数据库连接
            return "File not found", 404


@app.route('/singer/<id>.png')
def singer_img(id):
    covers_dir = os.path.join(base_dir, 'cover')
    cover_file_path = os.path.join(covers_dir, f'{id}.png')  # 使用 'id' 作为文件名

    if os.path.exists(cover_file_path):
        return send_file(cover_file_path, mimetype='image/png')

    cover_file_path1 = get_cover_from_file(id, covers_dir)
    if cover_file_path1:
        return send_file(cover_file_path1, mimetype='image/png')

    default_cover_path = os.path.join(covers_dir, '0.png')
    return send_file(default_cover_path, mimetype='image/png')


@app.route('/music_cover/<id>.png')
def cover_file(id):
    covers_dir = os.path.join(base_dir, 'cover')
    cover_file_path = os.path.join(covers_dir, f'{id}.png')  # 使用 'id' 作为文件名

    if os.path.exists(cover_file_path):
        return send_file(cover_file_path, mimetype='image/png')

    cover_file_path1 = get_cover_from_file(id, covers_dir)
    if cover_file_path1:
        return send_file(cover_file_path1, mimetype='image/png')

    default_cover_path = os.path.join(covers_dir, '0.png')
    return send_file(default_cover_path, mimetype='image/png')


def get_cover_from_file(id, covers_dir):
    cover_file_path = os.path.join(covers_dir, f'{id}.png')
    if os.path.exists(cover_file_path):
        return cover_file_path

    db = get_database_connection()
    cursor = db.cursor()
    query = "SELECT FilePath FROM songs WHERE SongID = %s;"
    cursor.execute(query, (id,))
    song_file_path = cursor.fetchone()

    if song_file_path:
        song_file_path = song_file_path[0]  # 提取路径字符串
        if os.path.exists(song_file_path):
            audio = MP3(song_file_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    cover_data = tag.data
                    cover_mime = tag.mime
                    if cover_mime == 'image/jpeg':  # 如果封面是JPEG格式，转换为PNG格式
                        img = Image.open(BytesIO(cover_data))
                        png_buffer = BytesIO()
                        img.save(png_buffer, format='PNG')
                        png_data = png_buffer.getvalue()
                        with open(cover_file_path, 'wb') as f:
                            f.write(png_data)
                        return cover_file_path
                    elif cover_mime == 'image/png':  # 如果封面已经是PNG格式，直接返回
                        with open(cover_file_path, 'wb') as f:
                            f.write(cover_data)
                        return cover_file_path

    return None


@app.route('/api/lrc/<song_id>')
def get_lrc(song_id):
    if song_id:
        try:
            db = get_database_connection()
            cursor = db.cursor()
            query = "SELECT Lyrics FROM songs WHERE SongID = %s;"
            cursor.execute(query, (song_id,))
            song_lrc = cursor.fetchone()
            if song_lrc and song_lrc[0]:
                lrc_filename = f"{song_id}.lrc"
                response = make_response(song_lrc[0])
                response.headers.set('Content-Disposition', 'attachment', filename=lrc_filename)
                response.headers.set('Content-Type', 'text/plain')
                return response
            else:
                cursor.close()
                cursor = db.cursor()
                query = "SELECT artists.Name, songs.Title FROM songs JOIN artists ON songs.ArtistID = artists.ArtistID WHERE SongID = %s;"
                cursor.execute(query, (song_id,))
                song_info = cursor.fetchone()
                if song_info:
                    artist = song_info[0]
                    title = song_info[1]
                    lrc_filename = f"{base_dir}/lrc/{artist} - {title}.lrc"

                    # 从文件中读取歌词内容
                    if os.path.exists(lrc_filename):
                        print(f"Reading lyrics from file: {lrc_filename}")
                        with open(lrc_filename, 'r', encoding='utf-8') as file:
                            lyrics = file.read()

                        # 更新数据库中的歌词内容
                        cursor = db.cursor()
                        update_query = "UPDATE songs SET Lyrics = %s WHERE SongID = %s;"
                        cursor.execute(update_query, (lyrics, song_id))
                        db.commit()
                        cursor.close()

                        response = make_response(lyrics)
                        response.headers.set('Content-Disposition', 'attachment', filename=f"{song_id}.lrc")
                        response.headers.set('Content-Type', 'text/plain')

                        return response
                    else:
                        lyrics_default = '[00:00.01]此歌曲暂无歌词'
                        response = make_response(lyrics_default)
                        response.headers.set('Content-Disposition', 'attachment', filename=f"{song_id}.lrc")
                        response.headers.set('Content-Type', 'text/plain')
                        return response

        except Exception as e:
            abort(500, description="An error occurred while retrieving lyrics.")

        finally:
            cursor.close()
            db.close()

    abort(404, description="Lyrics not found")


@app.route('/api/sidebar/')
def get_sidebar():
    dev_info = request.args.get('type', default='desket')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if dev_info == 'phone':
        sidebar_file = os.path.join(base_dir, 'sidebar', 'phone.html')
    else:
        sidebar_file = os.path.join(base_dir, 'sidebar', 'desket.html')

    try:
        with open(sidebar_file, 'r', encoding='gbk') as file:
            sidebar_content = file.read()
        return jsonify({"sidebar": sidebar_content})
    except FileNotFoundError:
        return jsonify({"error": "Sidebar file not found"}), 404


def song_name_list(ids):
    if ids:
        db = get_database_connection()
        cursor = db.cursor()
        try:
            print(ids)
            query = "SELECT songs.SongID, songs.Title, artists.Name FROM songs JOIN artists ON songs.ArtistID = artists.ArtistID WHERE songs.SongID IN ({})".format(
                ids)

            cursor.execute(query)
            song_data = cursor.fetchall()
            print(song_data)
            return song_data
        except Exception as e:
            return 'error', 404
        finally:
            cursor.close()
            db.close()


@app.route('/song/name/', methods=['GET'])
def song_name(id=0, pid=0, uid=0):
    id = request.args.get('id')
    pid = request.args.get('pid')
    if id and not pid:
        song_data = song_name_list(id)
        return jsonify(song_data)
    if pid:
        db = get_database_connection()
        cursor = db.cursor()
        try:
            query = "SELECT SongID FROM `playlist_songs` WHERE PlayListID = {}".format(
                pid)
            print(query)
            cursor.execute(query)
            list_data = cursor.fetchall()
            playlist = []
            for i in list_data:
                playlist.append(i[0])
            print(playlist)
            str_list = ','.join(str(x) for x in playlist)
            playlist_back = song_name_list(str_list)
            return jsonify(playlist_back)
        except Exception as e:
            return 'error', 404
        finally:
            cursor.close()
            db.close()
    if uid and not pid and not id:
        db = get_database_connection()
        cursor = db.cursor()
        try:
            query = "SELECT songs.SongID, songs.Title, artists.Name FROM songs JOIN artists ON songs.ArtistID = artists.ArtistID WHERE songs.ArtistID = {};".format(
                uid)
            cursor.execute(query)
            song_data = cursor.fetchall()
            return jsonify(song_data)
        except Exception as e:
            return 'error', 404
        finally:
            cursor.close()
            db.close()

    else:
        return jsonify({"error": "Invalid song id"})


@app.route('/album', methods=['GET'])
def album():
    album_id = request.args.get('id')
    data = {
        "id": album_id,
        "name": "Album " + album_id,
        "songs": []
    }
    return jsonify(data)


@app.route('/album/detail/dynamic')
def album_detail_dynamic():
    album_id = request.args.get('id')
    data = {
        "id": album_id,
        "likeCount": 100,
        "commentCount": 50
    }
    return jsonify(data)


@app.route('/album/sub', methods=['POST'])
def album_sub():
    action = "Subscribed" if request.args.get('t') == '1' else "Unsubscribed"
    data = {
        "status": action
    }
    return jsonify(data)


@app.route('/album/sublist')
def album_sublist():
    data = {
        "albums": []
    }
    return jsonify(data)


@app.route('/artists')
def artists():
    artist_id = request.args.get('id')
    data = {
        "artist": {"id": artist_id, "name": "Artist " + artist_id},
        "songs": []  # 示例热门歌曲数据
    }
    return jsonify(data)


@app.route('/artist/mv')
def artist_mv():
    data = {
        "mvs": []  # 示例MV数据
    }
    return jsonify(data)


@app.route('/artist/album')
def artist_album():
    data = {
        "albums": []
    }
    return jsonify(data)


@app.route('/artist/desc')
def artist_desc():
    artist_id = request.args.get('id')
    data = {
        "description": "Description for artist " + artist_id
    }
    return jsonify(data)


@app.route('/artist/detail')
def artist_detail():
    artist_id = request.args.get('id')
    data = {
        "artist": {"id": artist_id, "name": "Artist " + artist_id, "detail": "Some details here"}
    }
    return jsonify(data)


@app.route('/simi/artist')
def simi_artist():
    artist_id = request.args.get('id')
    data = {
        "similarArtists": []
    }
    return jsonify(data)


@app.route('/simi/playlist')
def simi_playlist():
    song_id = request.args.get('id')
    data = {
        "playlists": []
    }
    return jsonify(data)


@app.route('/recommend/resource')
def recommend_resource():
    data = {
        "playlists": [
            {"id": 1, "name": "Playlist 1"},
            {"id": 2, "name": "Playlist 2"},
        ]
    }
    return jsonify(data)


@app.route('/recommend/songs')
def recommend_songs():
    data = {
        "songs": [
            {"id": 1, "name": "Song 1"},
            {"id": 2, "name": "Song 2"},
        ]
    }
    return jsonify(data)


@app.route('/recommend/songs/dislike', methods=['POST'])
def dislike_song():
    song_id = request.args.get('id')
    data = {"status": "success", "message": f"Disliked song with ID{song_id}"}
    return jsonify(data)


@app.route('/history/recommend/songs')
def history_recommend_songs():
    data = {
        "dates": ["2020-06-21", "2020-06-20"]
    }
    return jsonify(data)


@app.route('/history/recommend/songs/detail')
def history_recommend_songs_detail():
    date = request.args.get('date')
    data = {
        "date": date,
        "songs": [
            {"id": 1, "name": "Historical Song 1"},
            {"id": 2, "name": "Historical Song 2"},
        ]
    }
    return jsonify(data)


@app.route('/personal_fm')
def personal_fm():
    data = {
        "tracks": [
            {"id": 1, "name": "Personal FM Track 1"},
            {"id": 2, "name": "Personal FM Track 2"},
        ]
    }
    return jsonify(data)


@app.route('/daily_signin', methods=['POST'])
def daily_signin():
    signin_type = request.args.get('type', '0')
    data = {"status": "success", "message": f"Signed in using method {signin_type}"}
    return jsonify(data)


@app.route('/like', methods=['POST'])
def like_song():
    song_id = request.args.get('id')
    like_status = request.args.get('like', True)
    action = "Liked" if like_status else "Unliked"
    data = {"status": "success", "message": f"{action} song with ID {song_id}"}
    return jsonify(data)


@app.route('/likelist')
def like_list():
    user_id = request.args.get('uid')
    data = {
        "user_id": user_id,
        "liked_songs": [{"id": 1}, {"id": 2}]
    }
    return jsonify(data)


@app.route('/fm_trash', methods=['POST'])
def fm_trash():
    song_id = request.args.get('id')
    data = {"status": "success", "message": f"Moved song with ID {song_id} to trash"}
    return jsonify(data)


@app.route('/top/album')
def top_album():
    # 这里仅为例子，实际参数处理可以更复杂
    year = request.args.get('year', '2021')
    month = request.args.get('month', '01')
    data = {
        "year": year,
        "month": month,
        "albums": [{"id": 1, "name": "Top Album 1"}, {"id": 2, "name": "Top Album 2"}]
    }
    return jsonify(data)


@app.route('/mv/all')
def mv_all():
    area = request.args.get('area', '全部')
    data = {
        "area": area,
        "mvs": [{"id": 1, "name": "MV 1"}, {"id": 2, "name": "MV 2"}]
    }
    return jsonify(data)


@app.route('/mv/first')
def mv_first():
    limit = request.args.get('limit', 30)
    data = {
        "limit": limit,
        "new_mvs": [{"id": 1, "name": "New MV 1"}, {"id": 2, "name": "New MV 2"}]
    }
    return jsonify(data)


@app.route('/mv/exclusive/rcmd')
def mv_exclusive_rcmd():
    limit = request.args.get('limit', 30)
    data = {
        "limit": limit,
        "exclusive_mvs": [{"id": 1, "name": "Exclusive MV 1"}, {"id": 2, "name": "Exclusive MV 2"}]
    }
    return jsonify(data)


@app.route('/personalized/mv')
def personalized_mv():
    data = {
        "recommend_mvs": [{"id": 1, "name": "Recommended MV 1"}, {"id": 2, "name": "Recommended MV 2"}]
    }
    return jsonify(data)


@app.route('/vip/growthpoint', methods=['GET'])
def get_vip_growthpoint():
    # 逻辑实现部分
    return jsonify({'message': '获取当前会员成长值'})


@app.route('/vip/growthpoint/details', methods=['GET'])
def get_vip_growthpoint_details():
    limit = request.args.get('limit', 20)
    offset = request.args.get('offset', 0)
    # 逻辑实现部分
    return jsonify({'message': '获取会员成长值领取记录'})


@app.route('/vip/tasks', methods=['GET'])
def get_vip_tasks():
    # 逻辑实现部分
    return jsonify({'message': '获取会员任务'})


@app.route('/vip/growthpoint/get', methods=['GET'])
def get_vip_growthpoint_rewards():
    ids = request.args.get('ids')
    # 逻辑实现部分
    return jsonify({'message': '获取已完成的会员任务的成长值奖励'})


@app.route('/artist/fans', methods=['GET'])
def get_artist_fans():
    artist_id = request.args.get('id')
    limit = request.args.get('limit', 10)
    offset = request.args.get('offset', 0)
    # 逻辑实现部分
    return jsonify({'message': '获取歌手粉丝'})


@app.route('/artist/follow/count', methods=['GET'])
def get_artist_fans_count():
    artist_id = request.args.get('id')
    # 逻辑实现部分
    return jsonify({'message': '获取歌手粉丝数量'})


@app.route('/digitalAlbum/detail', methods=['GET'])
def get_digital_album_detail():
    album_id = request.args.get('id')
    # 逻辑实现部分
    return jsonify({'message': '获取数字专辑信息'})


@app.route('/digitalAlbum/sales', methods=['GET'])
def get_digital_album_sales():
    ids = request.args.get('ids')
    # 逻辑实现部分
    return jsonify({'message': '获取数字专辑销量'})


@app.route('/msg/private', methods=['GET'])
def get_private_messages():
    limit = request.args.get('limit', 30)
    offset = request.args.get('offset', 0)
    # 逻辑实现部分
    return jsonify({'message': '获取私信'})


@app.route('/send/text', methods=['GET', 'POST'])
def send_text_message():
    user_ids = request.args.get('user_ids')
    msg = request.args.get('msg')
    # 逻辑实现部分
    return jsonify({'message': '发送文本私信'})


@app.route('/send/song', methods=['POST'])
def send_song_message():
    user_ids = request.form.get('user_ids')
    song_id = request.form.get('id')
    msg = request.form.get('msg')
    # 逻辑实现部分
    return jsonify({'message': '发送音乐私信'})


@app.route('/send/album', methods=['POST'])
def send_album_message():
    user_ids = request.form.get('user_ids')
    album_id = request.form.get('id')
    msg = request.form.get('msg')
    # 逻辑实现部分
    return jsonify({'message': '发送专辑私信'})


@app.route('/send/playlist', methods=['POST'])
def send_playlist_message():
    user_ids = request.form.get('user_ids')
    playlist_id = request.form.get('playlist')
    msg = request.form.get('msg')
    # 逻辑实现部分
    return jsonify({'message': '发送带歌单的私信'})


@app.route('/msg/recentcontact', methods=['GET'])
def get_recent_contact():
    # 逻辑实现部分
    return jsonify({'message': '获取最近联系人'})


@app.route('/msg/private/history', methods=['GET'])
def get_private_message_history():
    uid = request.args.get('uid')
    # 逻辑实现部分
    return jsonify({'message': '获取私信内容'})


@app.route('/msg/comments', methods=['GET'])
def get_comments():
    uid = request.args.get('uid')
    # 逻辑实现部分
    return jsonify({'message': '获取评论'})


@app.route('/msg/forwards', methods=['GET'])
def get_at_me():
    # 逻辑实现部分
    return jsonify({'message': '获取@我数据'})


@app.route('/msg/notices', methods=['GET'])
def get_notices():
    # 逻辑实现部分
    return jsonify({'message': '获取通知'})


@app.route('/setting', methods=['GET'])
def get_user_settings():
    # 逻辑实现部分
    return jsonify({'message': '获取用户设置'})


if __name__ == '__main__':
    test_database_connection()
    app.run(debug=True)
