import React, {useState, useEffect} from 'react';
import API_URL from '../../config';
import {Link} from "react-router-dom";
import {likeThisSong} from "../func/songMenu";

const PlayLists = ({pageType}) => {
    const [data, setData] = useState(null);
    const [visibleData, setVisibleData] = useState([]);
    const [loadMoreCount, setLoadMoreCount] = useState(28);

    useEffect(() => {
        fetch(API_URL + '/api/Recommend?pageType=' + pageType)
            .then(res => res.json())
            .then(data => {
                setData(data);
                setVisibleData(data.slice(0, 25)); // 初始加载25个歌曲
            })
            .catch(err => console.error('Error fetching data:', err));
    }, [pageType]);

    const loadMore = () => {
        setVisibleData(data.slice(0, visibleData.length + loadMoreCount));
    };

    let pageTitle = "歌单";
    if (pageType === 'al') {
        pageTitle = "专辑";
    }

    return (
        <div className="index-container" style={{height: '80%', display: 'flex', flexDirection: 'column'}}>
            {visibleData.length > 0 ? (
                <>
                    <h2>{pageTitle}</h2>
                    <ul style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between'}}>
                        {visibleData.map((item, index) => (
                            <li key={index} className="list_li" style={{width: '18%', marginBottom: '10px'}}>
                                <img
                                    className="cover_img"
                                    src={`${API_URL}/music_cover/${item[0]}.png`}
                                    alt="封面图片"
                                    style={{width: '100%', marginBottom: '5px'}}
                                />
                                <Link
                                    to={`/playlist?pid=${item[0]}&pageType=${pageType}&pTitle=${item[1]}&pRD=${item[2]}`}>
                                <span style={{textAlign: 'center'}}>
                                    <p>{item[1]}</p>
                                </span></Link>
                                <div style={{textAlign: 'center'}}>
                                    <p className='song_control'>
                                        <button onClick={() => likeThisSong(item[0])} className='button3'>♥</button>
                                    </p>
                                </div>
                            </li>
                        ))}
                    </ul>
                    {visibleData.length < data.length && (
                        <>
                            <p>已加载: {visibleData.length} 项</p>
                            <button onClick={loadMore} className='button4'>加载更多</button>
                            <p>到底了</p>
                        </>
                    )}
                </>
            ) : (
                <p>Loading...</p>
            )}
            <p className='bottomAlert'>前面的区域，以后再来探索吧！</p>
        </div>
    );
};

export default PlayLists;
