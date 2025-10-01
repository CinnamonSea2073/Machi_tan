from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_user_and_course_and_control_and_groq_flow():
    # register user
    r = client.post('/api/users/register', json={'name': 'alice'})
    assert r.status_code == 200
    user = r.json()
    assert 'user_id' in user

    uid = user['user_id']

    # create a course
    course_payload = {'id': 'course1', 'content': '<gpx>...</gpx>'}
    r = client.post('/api/courses/', json=course_payload)
    assert r.status_code == 200

    # set course of day
    r = client.post('/api/control/course_of_day', json={'course_id': 'course1'})
    assert r.status_code == 200
    r = client.get('/api/control/course_of_day')
    assert r.json().get('course_of_day') == 'course1'

    # set status
    r = client.post('/api/control/status', json={'status': '実行中'})
    assert r.status_code == 200
    r = client.get('/api/control/status')
    assert r.json().get('status') == '実行中'

    # create comment v2
    r = client.post('/api/comments_v2/', json={'user_id': uid, 'text': 'hi', 'genre': 'test'})
    assert r.status_code == 200
    cid = r.json().get('comment_id')

    # get comment
    r = client.get(f'/api/comments_v2/{cid}')
    assert r.status_code == 200

    # groq text
    r = client.post('/api/groq/text', json={'text': 'find me query'})
    assert r.status_code == 200
    assert 'output' in r.json()
