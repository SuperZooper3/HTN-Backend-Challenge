# Hack-the-North-Backend-Challenge
My Hack the North 2024 Backend Challenge submission.

## Setup

- Install Python 3.8 or later
- Create a virtual environment with `python -m venv venv` and activate it
- Install the required packages with `pip install -r requirements.txt`
- Initialize the database with `flask db init`, `flask db migrate`, and `flask db upgrade`
- Load the challenge data with `python load_data.py`
- Run the server with `python app.py`

## API Endpoints

### `GET /users`

Returns a json dictionary of all users in the database with their IDs as keys.

No parameters are required.

#### Example Request

Get all the users in the database.

```
GET /users
```

#### Example Response

A snippet of the response for all the users.

```json
{
    "1": {
        "company": "Jackson Ltd",
        "email": "lorettabrown@example.net",
        "name": "Breanna Dillon",
        "phone": "+1-924-116-7963",
        "skills": [
            {
                "rating": 4,
                "skill": "Swift"
            },
            {
                "rating": 1,
                "skill": "OpenCV"
            }
        ]
    },
    "2": {
        "company": "Moon, Mendoza and Carter",
        "email": "frederickkyle@example.org",
        "name": "Kimberly Wilkinson",
        "phone": "(186)579-0542",
        "skills": [
            {
                "rating": 4,
                "skill": "Foundation"
            },
            {
                "rating": 4,
                "skill": "Elixir"
            },
            {
                "rating": 2,
                "skill": "Fortran"
            },
            {
                "rating": 3,
                "skill": "Plotly"
            }
        ]
        ...
    }
}
```

### `GET /users/<int:user_id>`

Returns a json dictionary of the user with the specified ID.

Takes the user's ID as a parameter, and returns a 404 error if the user does not exist or the ID is invalid.

#### Example Request

Request to get the info for the user with ID 100.

```
GET /users/100
```

#### Example Response

The user with ID 100 is "Carolyn Gray", and we return their information.

```json
{
    "100": {
        "company": "Oliver LLC",
        "email": "matthew16@example.com",
        "name": "Carolyn Gray",
        "phone": "1234567890",
        "skills": [
            {
                "rating": 1,
                "skill": "Tachyons"
            },
            {
                "rating": 4,
                "skill": "Python"
            },
        ]
    }
}
```

### `PUT /users/<int:user_id>`

Updates fields of the user with the specified ID, and returns the updated user's information.

Takes the user's ID as a parameter, and a json body with the fields to update.

If fields exist (e.g. `name`, `email`, `phone`, `company`), they will be updated. If they do not exist, they will be ignored. All of these fields are optional and are treated as text.

If the field `skills` exists, all skills will either have their ratings updated or be added if they do not exist. Ratings must be integers between 1 and 5, or the request will return a 400 Bad Request.

Returns a 404 error if the user does not exist or the ID is invalid.

#### Example Request

Request to update the name of the user with ID 100 (from "Carolyn Gray") to "Carolyn Red". Note that the `fruits` field is ignored.

```
PUT /users/100
{
    "name": "Carolyn Red",
    "fruits": "apples",
}
```

#### Example Response

The user's name was updated from "Carolyn Gray" to "Carolyn Red".

```json
{
    "100": {
        "company": "Oliver LLC",
        "email": "matthew16@example.com",
        "name": "Carolyn Red",
        "phone": "1234567890",
        "skills": [
            {
                "rating": 1,
                "skill": "Tachyons"
            },
            {
                "rating": 4,
                "skill": "Python"
            },
        ]
    }
}
```

### `GET /skills`

Returns a json dictionary of all skills in the database with their name as keys, and their frequency and average rating as values.

Values are rounded to 2 decimal places, and are read from a cache to improve performance given the rarity of skill updates when compared to skill queries in a real-world scenario.

Optional arguments:

- `min_frequency` (int): The minimum frequency of the skill to be included in the response. Default is 0.
- `max_frequency` (int): The maximum frequency of the skill to be included in the response. Default is infinity (i.e. no maximum).
- `min_average_rating` (int): The minimum average rating of the skill to be included in the response. Default is 0.
- `max_average_rating` (int): The maximum average rating of the skill to be included in the response. Default is infinity (i.e. no maximum).

#### Example Request

Get all the skills with a frequency of at least 20 and an average rating of at least 3.

```
GET /skills?min_frequency=20&min_average_rating=3
```

#### Example Response

The only skill that meets the criteria is "Starlette" with a frequency of 21 and an average rating of 3.19.

```json
{
    "Starlette": {
        "average_rating": 3.19,
        "frequency": 21
    }
}
```

