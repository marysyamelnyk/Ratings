from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash
import pytest
from app import app
from models import db, User, ParsingResult
from flask_login import login_user
from unittest.mock import patch
from telegram_bot import send_telegram_message

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def create_user(client: FlaskClient):
    user = User(
        username="testuser",
        email="test@example.com",
        password=generate_password_hash("securepass123"),
        telegram_id=123456789
    )
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()

    with client.application.app_context():
        login_user(user)
    
    return user

@pytest.fixture
def create_custom_user(client: FlaskClient):
    def _create_user(username, email, telegram_id):
        user = User(
            username=username,
            email=email,
            password=generate_password_hash("pass123"),
            telegram_id=telegram_id
        )
        with client.application.app_context():
            db.session.add(user)
            db.session.commit()
        return user
    return _create_user

@pytest.fixture
def create_parsing_results(client: FlaskClient):
    result_1 = ParsingResult(
        user_email="test@example.com",
        url="http://example1.com",
        xpath="//div[@id='test1']",
        result="Test Result 1",
        timestamp="2025-04-29 12:00:00"
    )
    result_2 = ParsingResult(
        user_email="test@example.com",
        url="http://example2.com",
        xpath="//div[@id='test2']",
        result="Test Result 2",
        timestamp="2025-04-29 12:05:00"
    )
    with client.application.app_context():
        db.session.add(result_1)
        db.session.add(result_2)
        db.session.commit()

    return [result_1, result_2]

def test_register_success(client: FlaskClient):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepass123"
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert b"Registration successful" in response.data

def test_login_success(client: FlaskClient, create_user: User):
    data = {
        "email": "test@example.com",
        "password": "securepass123",
        "remember": "",
    }
    response = client.post("/login", data=data, follow_redirects=True)
    assert b"Login successful" in response.data

def test_delete_profile_success(client: FlaskClient, create_user: User):
    response = client.post('/delete_profile', follow_redirects=True)
    assert b"Your profile has been deleted successfully" in response.data

    with client.application.app_context():
        user_check = User.query.filter_by(email="test@example.com").first()
        assert user_check is None

def test_results(client: FlaskClient, create_user: User, create_parsing_results: list[ParsingResult]):
    response = client.get("/results")
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2
    assert json_data[0]["url"] == create_parsing_results[0].url
    assert json_data[1]["xpath"] == create_parsing_results[1].xpath

def test_delete_result_success(client: FlaskClient, create_user, create_parsing_results):
    result_to_delete = create_parsing_results[0]
    response = client.delete(f"/delete_result?url={result_to_delete.url}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Record deleted successfully" in response.data

    with client.application.app_context():
        deleted_result = ParsingResult.query.filter_by(url=result_to_delete.url).first()
        assert deleted_result is None

def test_send_telegram_message_success(client: FlaskClient, create_user: User):
    with patch("app.utils.bot.send_message") as mock_send:
        result = send_telegram_message("test@example.com", "Hello test")
        assert result is True
        mock_send.assert_called_once_with(123456789, "Hello test")

def test_send_telegram_message_no_user(client):
    with patch("app.utils.bot.send_message") as mock_send:
        result = send_telegram_message("nonexistent@example.com", "Hello test")
        assert result is False
        mock_send.assert_not_called()

def test_send_telegram_message_no_telegram_id(client: FlaskClient, create_custom_user):
    create_custom_user("noiduser", "noid@example.com", None)
    with patch("app.utils.bot.send_message") as mock_send:
        result = send_telegram_message("noid@example.com", "Hello test")
        assert result is False
        mock_send.assert_not_called()

def test_send_telegram_message_exception(client: FlaskClient, create_custom_user):
    create_custom_user("erroruser", "error@example.com", 987654321)
    with patch("app.utils.bot.send_message", side_effect=Exception("Mocked error")):
        result = send_telegram_message("error@example.com", "Hello test")
        assert result is False