# Hack-the-North-Backend-Challenge
My Hack the North 2024 Backend Challenge submission.

## Setup

- Install Python 3.8 or later
- Create a virtual environment with `python -m venv venv` and activate it
- Install the required packages with `pip install -r requirements.txt`
- Initialize the database with `flask db init`, `flask db migrate`, and `flask db upgrade`
- Load the challenge data with `python load_data.py`
- Run the server with `python app.py`

## Notes

- An effort was made to only make one query to the database for each API request, and to use the cache for the skills endpoint.
- All the query and update functions are in `app.py`, but could be moved to a separate file for better organization in a larger project.
- The `load_data.py` script is destructive and will delete all the data in the database before loading the challenge data.

## Database Schema

The database schema consists of three tables: `Participant`, `Skills`, and `CheckIn`.

The `Participant` table has the following columns:

- `id` (int): The unique identifier for the participant.
- `name` (str): The name of the participant.
- `company` (str): The company of the participant.
- `email` (str): The email of the participant.
- `phone` (str): The phone number of the participant.
- `checked_in` (bool): Whether the participant has checked in.
- `check_in_id` (int): The ID of the check-in event, if the participant has checked in.
- `skills` (list of `Skills`): The skills of the participant, modeled as a one-to-many relationship with the `Skills` table.

The `Skills` table has the following columns:

- `id` (int): The unique identifier for the skill.
- `name` (str): The name of the skill.
- `rating` (int): The rating of the participant for the skill.
- `participant_id` (int): The ID of the participant, modeling a many-to-one relationship with the `Participant` table.

The `CheckIn` table has the following columns:

- `id` (int): The unique identifier for the check-in event.
- `participant_id` (int): The ID of the participant, modeling a many-to-one relationship with the `Participant` table.
- `time` (int): The time of the check-in event.
- `volunteer_id` (int): The ID of the volunteer who checked in the participant (just a number for simplicity, but could be a foreign key to a `Volunteer` table in a real-world scenario).

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

### `GET /users/<int:participant_id>`

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

### `PUT /users/<int:participant_id>`

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

### `GET /checkin`

Checks if a user is checked in, and returns the check-in event if they are.

Takes the user's ID as a parameter, and returns a 404 error if the user does not exist.

#### Example Request

Check if the participant with ID 100 is checked in.

```
GET /checkin?participant_id=100
```

#### Example Response

The participant with ID 100 is not checked in.

```json
{
    "checked_in": false
}
```

### `POST /checkin`

Checks in a participant with a volunteer id, and returns the check-in event's details.

Takes the user's ID and volunteer's ID (just any interger for testing) in the json body, and returns a 404 error if the user does not exist, or a 400 error if the user is already checked in.

#### Example Request

Check in the participant with ID 100 with volunteer ID 1.

```
POST /checkin
{
    "participant_id": 100,
    "volunteer_id": 1
}
```

#### Example Response

The participant with ID 100 is checked in with volunteer ID 1.

```json
{
    "check_in_time": 1707689887,
    "checked_in": true,
    "volunteer_id": 1
}
```
