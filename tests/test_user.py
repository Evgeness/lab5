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
    # Проверяем, что возвращается сообщение об ошибке
    assert "detail" in response.json()

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''

    new_user = {
        "name": "Test User",
        "email": "testuser@example.com"
    }

    response = client.post("/api/v1/user", json=new_user)

    assert response.status_code == 201

    user_id = response.json()

    assert isinstance(user_id, int)
    
    # Проверяем, что пользователь действительно создан, получив его по email
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 200
    created_user = get_response.json()
    assert created_user['name'] == new_user['name']
    assert created_user['email'] == new_user['email']
    assert created_user['id'] == user_id

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_email = users[0]['email']
    user_data = {
        'name': 'Duplicate',
        'email': existing_email
    }
    response = client.post("/api/v1/user", json=user_data)
    # Ожидаем конфликт (409) или 400, в зависимости от реализации
    assert response.status_code in [400, 409]
    # Проверяем, что возвращено сообщение об ошибке
    assert "detail" in response.json()

def test_delete_user():
    '''Удаление пользователя'''

    new_user = {
        "name": "ToDelete",
        "email": "todelete@example.com"
    }

    create_response = client.post("/api/v1/user", json=new_user)

    assert create_response.status_code == 201

    user_id = create_response.json()

    delete_response = client.delete(f"/api/v1/user?id={user_id}")

    assert delete_response.status_code == 200
    
    # Удаляем пользователя (по email или по id - зависит от API)
    # Вариант 1: удаление по email
    delete_response = client.delete("/api/v1/user", params={'email': new_user['email']})
    assert delete_response.status_code == 204
    
    # Вариант 2: если API удаляет по id, используйте это:
    # delete_response = client.delete(f"/api/v1/user/{user_id}")
    # assert delete_response.status_code == 204
    
    # Проверяем, что пользователя больше нет
    get_after_delete = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_after_delete.status_code == 404
