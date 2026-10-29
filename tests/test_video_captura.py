import pytest
from scraper import validar_urls_videos, _feed_videos, _append_video_metrics, _empty_video

def test_urls_valid_and_duplicates():
    rows=validar_urls_videos("https://www.tiktok.com/@uno/video/1234567890123456789\nhttps://www.tiktok.com/@uno/video/1234567890123456789?lang=es")
    assert len(rows)==1
    assert rows[0]["usuario"]=="uno"
    assert rows[0]["video_id"]=="1234567890123456789"

@pytest.mark.parametrize("bad",["https://example.org/@uno/video/1234", "@uno", "https://www.tiktok.com/@uno"])
def test_urls_reject_other_links(bad):
    with pytest.raises(ValueError): validar_urls_videos(bad)

def test_public_feed_author_match():
    data={"itemList":[
        {"id":"1234567890", "author":{"uniqueId":"uno"},"stats":{"playCount":100,"diggCount":4}},
        {"id":"5678901234", "author":{"uniqueId":"otro"},"stats":{"playCount":2000,"diggCount":99}},
        {"id":"5678901235", "stats":{"playCount":2000,"diggCount":99}}]}
    result=_feed_videos(data,"uno")
    assert list(result)==["1234567890"]
    assert result["1234567890"]["vistas"]==100

def test_merge_preserves_missing_stats():
    video=_empty_video('uno','123','Enlace público')
    _append_video_metrics(video,{'vistas':10,'likes':0,'origen':'Pública'})
    _append_video_metrics(video,{'comentarios_cantidad':5,'origen':'DOM'})
    assert video['vistas']==10
    assert video['likes']==0
    assert video['comentarios_cantidad']==5

from scraper import videos_del_feed_incrustado

def test_post_list_profile_explicit_ids():
    state={"__DEFAULT_SCOPE__":{
        "webapp.user-detail":{"userInfo":{"user":{"id":"123","uniqueId":"uno"},"stats":{}}},
        "webapp.user-post":{"itemList":["9999999999999", "8888888888888"]},
    }}
    found=videos_del_feed_incrustado([state],"uno")
    assert set(found)=={"9999999999999","8888888888888"}
    assert videos_del_feed_incrustado([state],"otro")=={}
