import pytest

from scraper import (limpiar_usuario, usuarios_unicos, user_from_state,
                     videos_from_states, _video_from_item)


def test_input_names_and_urls():
    assert limpiar_usuario(' @un_perfil ') == 'un_perfil'
    assert limpiar_usuario('https://www.tiktok.com/@otra.cuenta') == 'otra.cuenta'
    assert usuarios_unicos('@uno, @DOS, @uno\n@tres') == ['uno','DOS','tres']
    with pytest.raises(ValueError):
        limpiar_usuario('https://example.com/@a')
    with pytest.raises(ValueError):
        limpiar_usuario('../archivo')


def test_state_matches_requested_account_only():
    fixture={"__DEFAULT_SCOPE__": {"webapp.user-detail": {"userInfo": {
        "user": {"uniqueId": "UNO", "nickname": "Uno"},
        "stats": {"followerCount": 45000}}}}}
    user,stats=user_from_state(fixture,'uno')
    assert user['nickname']=='Uno'
    assert stats['followerCount']==45000
    assert user_from_state(fixture,'otro')==({}, {})


def test_embedded_video_stats():
    data={"ItemModule": {"1234567890": {
        "id":"1234567890", "author":"uno", "desc":"prueba",
        "createTime":1700000000,
        "stats":{"playCount":12300,"diggCount":502,"commentCount":12}}}}
    vids=videos_from_states([data],"uno")
    assert vids["1234567890"]["likes"]==502
    assert vids["1234567890"]["vistas"]==12300
    assert videos_from_states([data],"otro")=={}


def test_no_other_author_stats():
    v=_video_from_item({'author':'someoneelse','stats':{'diggCount':99}},'12','uno','test')
    assert v=={}
