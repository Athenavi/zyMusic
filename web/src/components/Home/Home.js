import React, {useRef, useState, useEffect} from 'react';
import {useLocation} from "react-router-dom";
import SongDetail from '../SongDetail/SongDetail';
import CurrentList from "../CurrentList/CurrentList";
import API_URL from '../../config';
import './Home.css';
import {shareThisSong, likeThisSong} from "../func/songMenu";
import toggleVisable from "../func/toggleVisable";


// Playlist component
const Playlist = ({coverUrl, toggleVisable, likeThisSong, shareThisSong, playing, musicId}) => {
    const imgRef = useRef(null);

    useEffect(() => {
        const img = imgRef.current;
        if (img) {
            img.classList.toggle('rotating', playing);
        }
    }, [playing]);

    return (
        <div className="playlist">
            <div className="song" id='song'>
                <img
                    ref={imgRef}
                    src={coverUrl}
                    alt="封面图片"
                    style={{width: '100%'}}
                />
            </div>
            <div className='songBtn'>
                <button onClick={() => likeThisSong()}>收藏</button>
                {/*<button onClick={() => shareThisSong()}>分享</button>*/}
                <button onClick={() => toggleVisable('lrc_div')} id="btn_lrc_div">
                    词
                </button>
                <button onClick={() => toggleVisable('other_div')} id="btn_other_div">
                    ≡
                </button>
            </div>
        </div>
    );
};

function Home({playing, setPlaying, handleNextSong, token, audioRef}) {
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const [musicId, setMusicId] = useState(searchParams.get("id") || "0");
    const [playlistId, setPlaylistId] = useState(searchParams.get("pid") || "0");
    const [coverUrl, setCoverUrl] = useState(`${API_URL}/music_cover/${musicId}.png`);

    useEffect(() => {
        setMusicId(searchParams.get("id") || "0");
        setPlaylistId(searchParams.get("pid") || "0");
        setCoverUrl(`${API_URL}/music_cover/${musicId}.png`);
        localStorage.setItem('currentId', musicId);
    }, [location]);

    useEffect(() => {
        if (playing) {
            setCoverUrl(`${API_URL}/music_cover/${musicId}.png`);
        }
    }, [playing, musicId]);


    useEffect(() => {
        const audio = audioRef.current;
        const lyricsDiv = document.getElementById('lyrics');
        const lyricLines = lyricsDiv.getElementsByTagName('p');
        let activeLine = null;

        const handleTimeUpdate = () => {
            const url = new URL(audio.src);
            const currentMusicId = url.pathname.split('/')[2].split('.')[0];

            // 检查播放器 URL 中的音乐 ID 是否和歌词页面的 ID 相匹配
            if (currentMusicId !== musicId) {
                return;
            }

            const currentTime = audio.currentTime;

            for (let i = 0; i < lyricLines.length; i++) {
                const timeStr = lyricLines[i].id.split('_')[1];
                const lineTime = parseLyricTime(timeStr);

                if (currentTime >= lineTime) {
                    if (activeLine) {
                        activeLine.classList.remove('active');
                    }
                    activeLine = lyricLines[i];
                    activeLine.classList.add('active');
                } else {
                    break;
                }
            }

            if (activeLine) {
                activeLine.scrollIntoView({behavior: "smooth", block: "center"});
            }
        };

        function parseLyricTime(timeStr) {
            const parts = timeStr.split(':');
            const minutes = parseInt(parts[0], 10);
            const seconds = parseFloat(parts[1]);
            return minutes * 60 + seconds;
        }

        audio.addEventListener('timeupdate', handleTimeUpdate);

        return () => {
            audio.removeEventListener('timeupdate', handleTimeUpdate);
        };
    }, [musicId, playing, audioRef]);

    return (
        <div>
            <div className='cr'>
                © CopyRight 2002-2024, 7trees.cn
            </div>
            <div className="flex-container">
                <Playlist
                    coverUrl={coverUrl}
                    toggleVisable={toggleVisable}
                    likeThisSong={likeThisSong}
                    shareThisSong={shareThisSong}
                    playing={playing}
                    musicId={musicId}
                />

                <div className='lrc_div' id='lrc_div' key={musicId}>
                    <SongDetail musicId={musicId} key={musicId}/>
                </div>

                <div className='other_div' id='other_div'>
                    <CurrentList pid={playlistId} setMusicId={setMusicId} handleNextSong={handleNextSong}
                                 key={musicId} toggleVisable={toggleVisable}/>
                </div>
            </div>
        </div>
    );
}

export default Home;