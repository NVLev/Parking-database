<h1>Flask-приложение для работы парковки</h1>
<p></p>
Описаны ORM-модели клиента, парковки и лога въезда-выезда с парковки
<p></p>
<p>Реализованы следующие функции:</p>
<ul style="list-style: none;">
  <li>Получение списка клиентов</li>
  <li>Добавление клиента</li>
  <li>Добавление парковки</li>
  <li>Чек-ин - фиксация времени заезда, уменьшение количества свободных мест</li>
  <li>Чек-аут - фиксация времени выезда, привязка кредитной карты, увеличение количества свободных мест</li>
  </ul>
<p>Реализованы тесты pytest</p>  
<p></p>
  Установка зависимостей - poetry add requirements.txt
  <p></p>
  Запуск базы данных - docker-compose up -d
  <p></p>
  Запуск приложения: poetry run python main.py
  <p></p>
  Документация на эндпоинте /docs
<p></p>
<h2>Стек проекта:</h2>
Flask, Application Factory, Poetry, PostgreSQL, SQLAlchemy, Alembic, Pytest, Factory Boy, Docker-compose 
<p></p>
<b>Особенности:</b>
<p>Документация на финском языке</p>
