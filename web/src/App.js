// App.js
import React, {useEffect, useRef, useState} from 'react';
import {BrowserRouter as Router, Link, Route, Routes} from 'react-router-dom';
import Home from './components/Home/Home';
import Login from './components/Login/Login';
import Register from './components/Register/Register';
import TopList from "./components/TopList/TopList";
import Index from "./components/Index/Index";
import PlayLists from "./components/PlayLists/PlayLists";
import './App.css'
import PlaylistDetail from "./components/playlistDetail/playlistDetail";
import API_URL from "./config";
import Logout from "./components/Login/Logout";
import Singer from "./components/Singer/Singer";
import toggleVisable from './components/func/toggleVisable'


function App() {
    const [token, setToken] = useState(localStorage.getItem('token') || null);
    const audioRef = useRef(null);
    const [playing, setPlaying] = useState(false);
    const [musicId, setMusicId] = useState("0");

    useEffect(() => {
        document.title = "zyMusic"; // 设置浏览器标签的标题
    }, []); // 使用空数组作为第二个参数，确保这段代码只在组件挂载时执行一次


    useEffect(() => {
        localStorage.setItem('token', token);
    }, [token]);

    const handleNextSong = (nextMusicId) => {
        setMusicId(nextMusicId);

        audioRef.current?.pause();
        audioRef.current.src = API_URL + `/music/${nextMusicId}.mp3`;

        // 添加事件监听器，等待新的src加载完成再播放
        audioRef.current.addEventListener('canplaythrough', () => {
            audioRef.current.play().then(() => {
                setPlaying(true);
            });
        });
    };

    useEffect(() => {
        const handleNextSongOnEnded = () => {
            const currentPlaylist = JSON.parse(localStorage.getItem('currentPlaylist')) || {播放列表: []};
            const playlist = currentPlaylist['播放列表'];
            const currentIndex = playlist.findIndex(item => item.id === musicId);

            if (currentIndex !== -1 && currentIndex < playlist.length - 1) {
                const nextMusicId = playlist[currentIndex + 1].id;
                handleNextSong(nextMusicId);
            } else {
                alert("已经是最后一首歌曲");
            }
        };

        audioRef.current.addEventListener('ended', handleNextSongOnEnded);

        return () => {
            audioRef.current.removeEventListener('ended', handleNextSongOnEnded);
        };
    }, [musicId]);


    return (
        <Router>
            <nav id='nav'>
                <Link to="/"><img src="https://7trees.cn/zyImg/qks2862/chenIn.png" alt="Logo" className="logo"/> zyMusic</Link>
                <Link to="/discover/playlists">发现音乐</Link>
                {token ? (
                    <Link to="/my">我</Link>
                ) : (
                    <Link to="/login">登录</Link>
                )}
            </nav>
            <header>
                <div className="secondMenu">
                    <Link to="/toplist">排行榜</Link>
                    <Link to="/discover/singer">歌手</Link>
                    <Link to="/discover/album">专辑</Link>
                    <Link to="/song">播放</Link>
                </div>
            </header>
            <div className='player'>
                <audio
                    ref={audioRef}
                    controls
                    autoPlay
                    onPlay={() => setPlaying(true)}
                    onPause={() => setPlaying(false)}
                    onEnded={handleNextSong}
                    src={API_URL + `/music/` + musicId + '.mp3'}

                >
                    Your browser does not support the audio element.
                </audio>
                <button onClick={() => toggleVisable('other_div')} id="btn_other_div2">
                    ≡
                </button>
            </div>
            <Routes>
                <Route path="/" element={<Index token={token}/>}/>
                <Route path="/song" element={<Home token={token} playing={playing} setPlaying={setPlaying}
                                                   handleNextSong={handleNextSong} setMusicId={setMusicId}
                                                   audioRef={audioRef}/>}/>
                <Route path="/toplist" element={<TopList token={token}/>}/>
                <Route path="/discover/singer" element={<Singer setMusicId={setMusicId}/>}/>
                <Route path="/discover/playlists" element={<PlayLists token={token} pageType="pl"/>}/>
                <Route path="/discover/album" element={<PlayLists token={token} pageType="al"/>}/>
                <Route path="/playlist"
                       element={<PlaylistDetail token={token} setMusicId={setMusicId} pageType="pl"/>}/>
                <Route path="/album" element={<PlaylistDetail token={token} setMusicId={setMusicId} pageType="al"/>}/>
                <Route path="/login" element={<Login/>}/>
                <Route path="/register" element={<Register/>}/>
                <Route path="/logout" element={<Logout/>}/>
            </Routes>
        </Router>
    );
}

export default App;

