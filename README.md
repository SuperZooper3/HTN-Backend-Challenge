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
```
GET /users
```

#### Example Response
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
```

### `GET /users/<int:user_id>`

Returns a json dictionary of the user with the specified ID.

Takes the user's ID as a parameter, and returns a 404 error if the user does not exist or the ID is invalid.

#### Example Request
```
GET /users/100
```

#### Example Response
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

Updates fields of the user with the specified ID.

Takes the user's ID as a parameter, and a json body with the fields to update.

If fields exist (e.g. `name`, `email`, `phone`, `company`), they will be updated. If they do not exist, they will be ignored. All fields are optional and are treated as text.

If the field `skills` exists, all skills will either have their ratings updated or be added if they do not exist. Ratings must be integers between 1 and 5, or the request will return a 400 Bad Request.
