# Control Work 
## Описание проекта
Это учебный проект на Django REST Framework, реализующий блог с постами и комментариями.
## Функциональные требования
### 1. Модели
- **User** — стандартная модель пользователя Django.
- **Post**  
  - id  
  - author (ForeignKey → User)  
  - title  
  - body  
  - created_at  
  - updated_at  
  - is_published
- **Comment**  
  - id  
  - post (ForeignKey → Post)  
  - author (ForeignKey → User)  
  - body  
  - created_at  
  - updated_at  
  - is_approved  
### 2. Аутентификация
- Token authentication через `rest_framework.authtoken`.
- Гостям доступно только чтение опубликованных постов.
### 3. Эндпоинты
#### Посты
- **GET /api/v1/posts/** — список постов (доступно всем, включая гостей)
- **POST /api/v1/posts/** — создание поста (только авторизованный)
- **GET /api/v1/posts/{id}/** — подробный просмотр поста
- **PUT/DELETE /api/v1/posts/{id}/** — только автор поста
#### Комментарии
- **GET /api/v1/posts/{id}/comments/** — список комментариев (доступно всем)
- **POST /api/v1/posts/{id}/comments/** — добавить комментарий (только авторизованным)
- **PUT/DELETE /api/v1/posts/{id}/comments/{comment_id}/** — только автор комментария
### 4. Права доступа
- Только владелец может менять/удалять свои посты и комментарии.
### 5. Пагинация
- Пагинация постов по 5 элементов на страницу.
### 6. Тесты
- Тесты пока не реализованы.
### 7. Документация
- Swagger доступен через:
  - `/swagger/`

## Запуск проекта
1. Клонируем репозиторий:
```bash
git clone https://github.com/aigerim2006/control_work_month_5.git
cd CONTROL_WORK
source venv/bin/activate  
python manage.py runserver
