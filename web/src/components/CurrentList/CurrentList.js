import React, {useState, useEffect} from 'react';
import {Link} from "react-router-dom";
import API_URL from '../../config';

function CurrentList({pid, setMusicId, handleNextSong, toggleVisable}) {
    const [data, setData] = useState(null);

    let fetchData = async () => {
        try {
            const res = await fetch(API_URL + `/api/userSongList?pid=1`);
            const responseData = await res.json();
            const convertedData = convertData(responseData);
            setData(convertedData);
            localStorage.setItem('currentPlaylist', JSON.stringify(convertedData));
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    const convertData = (data) => {
        return {
            "播放列表": data["播放列表"].map(item => {
                return {
                    id: item[0],
                    title: item[1] || "Unknown Title",
                    artist: item[2] || "Unknown Artist"
                };
            })
        };
    };

    useEffect(() => {
        const cachedData = localStorage.getItem('currentPlaylist');
        if (cachedData) {
            setData(JSON.parse(cachedData));
        } else {
            fetchData();
        }
    }, []);

    const removeFromPlaylist = (id) => {
        setData(prevData => {
            const updatedData = {...prevData};
            updatedData["播放列表"] = updatedData["播放列表"].filter(item => item.id !== id);
            localStorage.setItem('currentPlaylist', JSON.stringify(updatedData));
            return updatedData;
        });
    };

    const moveFromPlaylist = (id, up) => {
        setData(prevData => {
            const updatedData = {...prevData};
            const index = updatedData["播放列表"].findIndex(item => item.id === id);
            if (index !== -1) {
                const newIndex = up ? index - 1 : index + 1;
                if (newIndex >= 0 && newIndex < updatedData["播放列表"].length) {
                    [updatedData["播放列表"][index], updatedData["播放列表"][newIndex]] = [updatedData["播放列表"][newIndex], updatedData["播放列表"][index]];
                    localStorage.setItem('currentPlaylist', JSON.stringify(updatedData));
                }
            }
            return updatedData;
        });
    };


    const scrollToTop = () => {
        document.getElementById('other_div').scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    };


    return (
        <div className="index-container" id='currentPlayList'>
            {data ? (
                <>
                    <ul style={{maxHeight: '75vh'}}>
                        {Object.entries(data).map(([key, value]) => (
                            <li key={key} style={{background: "transparent"}}>
                                <a onClick={() => toggleVisable('other_div')}>
                                    ≡ {key}
                                </a>
                                <ol style={{maxHeight: '65vh'}}>
                                    {value.map((item) => (
                                        <li key={item.id}>
                                            <Link to={`/song?id=${item.id}`} onClick={() => {
                                                setMusicId(item.id);
                                                handleNextSong(item.id);
                                            }}><p>{item.artist} - {item.title}</p></Link>
                                            <div className='songlist_control'>
                                                <button
                                                    onClick={() => moveFromPlaylist(item.id, true)}>👆
                                                </button>
                                                <button
                                                    onClick={() => moveFromPlaylist(item.id, false)}>👇
                                                </button>
                                                <button
                                                    onClick={() => removeFromPlaylist(item.id)}>⭕
                                                </button>
                                                {item.id % 5 === 0 ? (
                                                    <a onClick={scrollToTop}>↑回到顶部</a>
                                                ) : (
                                                    <></>
                                                )
                                                }

                                            </div>
                                        </li>
                                    ))}
                                </ol>
                            </li>
                        ))}
                    </ul>
                </>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
}

export default CurrentList;