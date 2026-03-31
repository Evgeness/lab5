from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Существующие пользователи (начальное состояние)
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'nonexistent@example.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'Test User',
        'email': 'testuser@example.com'
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == new_user['name']
    assert data['email'] == new_user['email']
    assert 'id' in data

    # Проверяем, что пользователь действительно создан
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 200
    assert get_response.json()['email'] == new_user['email']

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_email = users[0]['email']
    user_data = {
        'name': 'Duplicate',
        'email': existing_email
    }
    response = client.post("/api/v1/user", json=user_data)
    # Ожидаем конфликт (409) или 400, в зависимости от реализации
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создаём временного пользователя
    new_user = {
        'name': 'ToDelete',
        'email': 'todelete@example.com'
    }
    create_response = client.post("/api/v1/user", json=new_user)
    assert create_response.status_code == 201
    user_id = create_response.json()['id']

    # Удаляем по email
    delete_response = client.delete("/api/v1/user", params={'email': new_user['email']})
    assert delete_response.status_code == 204

    # Проверяем, что пользователя больше нет
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 404