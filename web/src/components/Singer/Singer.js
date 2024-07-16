import React, {useState, useEffect} from 'react';
import API_URL from '../../config';
import {Link, useLocation} from "react-router-dom";
import removeFromPlaylist from "../func/removeFromPlaylist";
import addToPlaylist from "../func/addToPlaylist";
import {likeThisSong} from "../func/songMenu";

const SingerDetail = () => {
    const [data, setData] = useState(null);
    const [visibleItems, setVisibleItems] = useState(60);
    const [showMore, setShowMore] = useState(true);
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const name = searchParams.get('name') || "";
    let singerId = searchParams.get("uid") || "0";

    const fetchData = async (singerId) => {
        try {
            const res = await fetch(API_URL + `/api/singer?uid=` + singerId);
            const responseData = await res.json();
            const convertedData = convertData(responseData);
            setData(convertedData);
            localStorage.setItem('singerPlaylist_' + singerId, JSON.stringify(convertedData));
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    useEffect(() => {
        const cachedData = localStorage.getItem('singerPlaylist_' + singerId);
        if (cachedData) {
            setData(JSON.parse(cachedData));
        } else {
            fetchData(singerId);
        }
    }, [location, singerId]);

    const convertData = (data) => {
        return {
            "artists": data["歌手"].map(item => {
                return {
                    id: item[0],
                    artist: item[1] || "Unknown Artist"
                };
            })
        };
    };

    const loadMoreItems = () => {
        setVisibleItems(prev => prev + 40);
    };

    useEffect(() => {
        if (data && data.artists.length <= visibleItems) {
            setShowMore(false);
        } else {
            setShowMore(true);
        }
    }, [visibleItems, data]);

    return (
        <>
            <div className="index-container">
                {data ? (
                    <>
                        <ul>
                            {Object.entries(data).map(([key, value]) => (
                                <li key={key} className="list_container" style={{width: '100%', marginBottom: '10px'}}>
                                    <h3>{name}</h3>
                                    <ol style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between'}}>
                                        {value && value.slice(0, visibleItems).map((item) => (
                                            <li key={item.id} className="list_container"
                                                style={{width: '16%', margin: '7px', background: 'cornflowerblue'}}>
                                                {
                                                    singerId === '0' ? (
                                                        <>
                                                            <img
                                                                className="cover_img"
                                                                src={`${API_URL}/singer/${item.id}.png`}
                                                                alt="封面图片"
                                                                style={{width: '50%', marginBottom: '5px'}}
                                                            />
                                                            <Link
                                                                to={`/discover/singer?uid=${item.id}&name=${item.artist}`}>
                                                                <p>{item.artist}</p>
                                                            </Link>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <img
                                                                className="cover_img"
                                                                src={`${API_URL}/music_cover/${item.id}.png`}
                                                                alt="封面图片"
                                                                style={{width: '20%', marginBottom: '5px'}}
                                                            />
                                                            <Link
                                                                to={`/song?id=${item.id}&name=${item.artist}`}>
                                                                <p>{item.artist}</p>
                                                            </Link>
                                                            <div>
                                                                <p className='song_control'>
                                                                    <button onClick={() => removeFromPlaylist(item[0])}
                                                                            className='button1'>-
                                                                    </button>
                                                                    <button onClick={() => addToPlaylist({
                                                                        id: item.id,
                                                                        artist: name,
                                                                        title: item.artist
                                                                    })} className='button2'>+
                                                                    </button>
                                                                    <button onClick={() => likeThisSong(item[0])}
                                                                            className='button3'>♥
                                                                    </button>
                                                                </p>
                                                            </div>


                                                        </>

                                                    )
                                                }
                                            </li>
                                        ))}
                                    </ol>
                                </li>
                            ))}
                        </ul>
                        {showMore ? (
                            <button onClick={loadMoreItems} id='btn_load_more'
                                    style={{marginBottom: '45px'}}>查看更多</button>
                        ) : (
                            <p style={{marginBottom: '45px'}}>已经到底了呢</p>
                        )}
                    </>
                ) : (
                    <p>Loading...</p>
                )}
            </div>
        </>
    );
};

export default SingerDetail;
