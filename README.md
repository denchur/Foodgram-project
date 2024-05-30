# foodgram
Проект 'FOODGRAM' разработан для публикации рецептов. Вы можете подписаться на автора, чьи рецепты вам нравятся,
добавлять рецепты в избранное, а также в список покупок, откуда легко и удобно можно скачать список и пойти в магазин за продуктами.
## Установка

### Cклонируйте репозиторий GitHub
- `git clone git@github.com:Ваш_аккаунт/<Имя проекта>.git`

### Создайте файл .env в директории /infra и внесити в него данные
```
# Файл .env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DB_HOST=
DB_PORT=5432 
SECRET_KEY=
DEBUG_KEY=
ALLOWED_HOSTS=
```

### Для запуска перейдите в директорию /infra/
```
docker compose-up
```

## Использование
- Получение списка всех рецептов:
```
  GET /api/recipes/
```
```
{
  "count": 7,
  "next": "http://localhost:8000/api/recipes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 14,
      "name": "Рецепт",
      "image": "http://localhost:8000/media/images/b957c2c2-645a-4ace-8387-098098aebc6b.jpg",
      "text": "sda",
      "cooking_time": 22,
      "author": {
        "email": "admin@ya.ru",
        "id": 1,
        "username": "admin",
        "first_name": "Имя",
        "last_name": "Фамиля",
        "is_subscribed": false
      },
      "tags": [
        {
          "id": 1,
          "name": "Завтрак",
          "color": "#ffdd00",
          "slug": "breakfast"
        },
        {
          "id": 2,
          "name": "Обед",
          "color": "#008000",
          "slug": "diar"
        }
      ],
      "ingredients": [
        {
          "id": 4,
          "name": "Молоко",
          "measurement_unit": "мл",
          "amount": 500
        }
      ],
      "is_favorited": false,
      "is_in_shopping_cart": false
    },
    ...
  ]
```
- Получение конкретного рецепта:
```
  GET /api/recipes/1/
```
```  
{
  "id": 1,
  "name": "Пицца",
  "image": "http://localhost:8000/media/images/b827eacc-3b9c-47dd-ad7f-b8a0e3592022.jpg",
  "text": "Рецепт",
  "cooking_time": 100,
  "author": {
    "email": "admin@ya.ru",
    "id": 1,
    "username": "admin",
    "first_name": "имя",
    "last_name": "Фамилия",
    "is_subscribed": false
  },
  "tags": [
    {
      "id": 1,
      "name": "Завтрак",
      "color": "#ffdd00",
      "slug": "breakfast"
    }
  ],
  "ingredients": [
    {
      "id": 1,
      "name": "Мука",
      "measurement_unit": "г",
      "amount": 100
    },
    {
      "id": 2,
      "name": "Сыр",
      "measurement_unit": "г",
      "amount": 100
    },
    {
      "id": 3,
      "name": "Колбаса",
      "measurement_unit": "г",
      "amount": 50
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true
}
```
- Создание нового рецепта:
```
  AUTHORIZATIONS: Token Ваш Токее
  POST /api/recipes/ {
    "tags": [1,2],
    "name": "Название",
    "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvDMAAAAASUVORK5CYII=",
    "text": "description",
    "cooking_time": 20,
    "ingredients": [
      {
        "id":2,
        "amount":1
      },
      {
        "id":1,
        "amount":1
      }

    ]
}
```

```
  {
  "id": 15,
  "name": "Название",
  "image": "http://127.0.0.1:8000/media/images/94d12713-c416-4928-9827-0506b3eaa174.png",
  "text": "description",
  "cooking_time": 20,
  "author": {
    "email": "admin@ya.ru",
    "id": 1,
    "username": "admin",
    "first_name": "Имя",
    "last_name": "Фамилия",
    "is_subscribed": false
  },
  "tags": [
    1,
    2
  ],
  "ingredients": [
    {
      "id": 2,
      "name": "Сыр",
      "measurement_unit": "г",
      "amount": 1
    },
    {
      "id": 1,
      "name": "Мука",
      "measurement_unit": "г",
      "amount": 1
    }
  ]
}
```
## Участие в разработке
    Denchur
