Review Tracker

Review Tracker – це веб-застосунок для збору, аналізу та відстеження відгуків користувачів. Проєкт розроблений на Flask та використовує SQLite для управління базою даних. Додаток підтримує реєстрацію, автентифікацію та логування помилок, а також розгорнутий на AWS EC2.

Функціонал
- Реєстрація та авторизація користувачів
- Збір та збереження відгуків у базі даних
- Фільтрація та сортування відгуків
- Логування подій та помилок
- Деплой на AWS EC2

Використані технології
- Backend: Python, Flask
- Database: SQLite (sqlite3)
- Frontend: HTML, CSS, Bootstrap
- Deployment: AWS EC2

Встановлення та запуск
1. Клонування репозиторію
```bash
git clone https://github.com/yourusername/review-tracker.git
cd review-tracker
```

2. Створення віртуального середовища та встановлення залежностей
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
venv\Scripts\activate  # Для Windows
pip install -r requirements.txt
```

3. Налаштування бази даних
Змініть `.env.example` на `.env` та вкажіть свої налаштування бази даних:
```
DATABASE_URL=sqlite:///review_tracker.db
SECRET_KEY=your_secret_key
```

Створіть базу даних:
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

4. Запуск застосунку
```bash
flask run
```

Застосунок буде доступний за наступним посиланням:
http://3.82.226.65/

Контакти
Якщо у вас є питання або пропозиції, зв'яжіться зі мною через GitHub або email: marynka555@gmail.com.