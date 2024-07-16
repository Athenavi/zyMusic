import React, {useState, useEffect} from 'react';
import API_URL from '../../config';
import {Link} from "react-router-dom";
import addToPlaylist from "../func/addToPlaylist";
import removeFromPlaylist from "../func/removeFromPlaylist";
import {shareThisSong, likeThisSong} from "../func/songMenu";
import './Toplist.css';

const TopList = () => {
    const [data, setData] = useState(null);
    const [visibleData, setVisibleData] = useState([]);
    const [loadMoreCount, setLoadMoreCount] = useState(30); // 设置每次加载的数量

    useEffect(() => {
        fetch(API_URL + '/api/toplist')
            .then(res => res.json())
            .then(data => {
                setData(data);
                setVisibleData(data.slice(0, 30));
            })
            .catch(err => console.error('Error fetching data:', err)); // add error handling
    }, []);

    const loadMore = () => {
        setVisibleData(data.slice(0, visibleData.length + loadMoreCount));
    };

    return (
        <div className="index-container" style={{height: '80%', display: 'flex', flexDirection: 'column'}}>
            {visibleData.length > 0 ? (
                <>
                    <h2>排行榜</h2>
                    <ul style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between'}}>
                        {visibleData.map((item, index) => (
                            <li key={index} className="list_li" style={{width: '18%', marginBottom: '10px'}}>
                                <img
                                    className="cover_img"
                                    src={`${API_URL}/music_cover/${item[0]}.png`}
                                    alt="封面图片"
                                    style={{width: '25%', marginBottom: '5px'}}
                                />
                                <Link to={`/song?id=${item[0]}`}>{item[2]}<p>{item[1]}</p></Link>
                                <div>
                                    <p className='song_control'>
                                        <button onClick={() => removeFromPlaylist(item[0])} class='button1'>-</button>
                                        <button onClick={() => addToPlaylist({
                                            id: item[0],
                                            artist: item[1],
                                            title: item[2]
                                        })} className='button2'>+
                                        </button>
                                        <button onClick={() => likeThisSong(item[0])} className='button3'>♥</button>
                                    </p>
                                </div>
                                <br/>
                            </li>

                        ))}
                    </ul>
                    {visibleData.length < data.length && (
                        <>
                            <p>已加载: {visibleData.length} 项</p>
                            <button onClick={loadMore} className='button4'>加载更多</button>
                        </>
                    )}
                </>
            ) : (
                <p>Loading...</p> // show loading state
            )}
            <p className='bottomAlert'>前面的区域，以后再来探索吧！</p>
        </div>
    );
};

export default TopList;
