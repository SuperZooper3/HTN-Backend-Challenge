# Hack the North Backend Challenge 😋🧋 Boba Edition

My Hack the North 2024 Backend Challenge submission. If you have any questions or issues, don't hesitate to reach out to me on discord at `@superzooper`.

I think HTN would be 10x better if there was a free boba delivery service, so the tactical `/boba` endpoint has been included.

## Setup

- Install Python 3.8 or later
- Create a virtual environment with `python -m venv venv` and activate it
- Install the required packages with `pip install -r requirements.txt`
- Initialize the database with `flask db init`, `flask db migrate`, and `flask db upgrade`
- Load the challenge data with `python load_data.py`
- Run the server with `python run.py`

## App Structure

- `run.py`: The entry point for the Flask app.
- `config.py`: The configuration for the Flask app with constants.
- `app/`: The main app package.
  - `__init__.py`: The app factory and the database and cache setup, getters and setters.
  - `models/`: The database models for the app.
    - `models.py`: The database models for the app.
  - `routes/`: The routes for the app.
    - `participant_routes.py`: The routes for the participant and checkin endpoints.
    - `boba_routes.py`: The routes for the boba endpoints.
    - `skill_routes.py`: The routes for the skill endpoints.
  - `services/`: The services for the app and database interactions.
    - `participant_service.py`: The service for the participant and checkin like registration and updating participant info.
    - `boba_service.py`: The service for the boba endpoints like placing or updating orders.
    - `skill_service.py`: The service for the skill like comparison checks.
  - `utils/`: The utility functions for the app.
    - `cache_utils.py`: Functions to generate and update the cache.

## Tools

- `load_data.py`: A script to load the challenge data into the database from `HTN_2023_BE_Challenge_Data.json`.
- `investigate_data.ipynb`: A Jupyter notebook to investigate the challenge data and make decisions for the database schema.
- `HTN Challenge.postman_collection.json`: A Postman collection with all the API requests and responses for the app.

## Notes

- An effort was made to only make one query to the database for each API request, and to use the cache for the skills endpoint.
- All the query and update functions are in `app.py`, but could be moved to a separate file for better organization in a larger project.
- The `load_data.py` script is destructive and will delete all the data in the database before loading the challenge data.
- All endpoints were tested with Postman and the responses were manually validated with the expected responses in the challenge description and in this specifcation. The test are included in `HTN Challenge.postman_collection.json` and have many more examples than the ones in this README.

## Database Schema

The database schema consists of four tables: `Participant`, `Skills`, `CheckIn` and `Boba`.

The `Participant` table has the following columns:

- `id` (int): The unique identifier for the participant.
- `name` (str): The name of the participant.
- `company` (str): The company of the participant.
- `email` (str): The email of the participant. This is also treated as a unique field to prevent duplicate registrations, so some of the 1000 example participants aren't registered in the database to avoid duplicate emails.
- `phone` (str): The phone number of the participant.
- `checked_in` (bool): Whether the participant has checked in.
- `check_in_id` (int): The ID of the check-in event, if the participant has checked in.
- `skills` (list of `Skills`): The skills of the participant, modeled as a one-to-many relationship with the `Skills` table.
- `boba_orders` (list of `Boba`): The boba orders of the participant, modeled as a one-to-many relationship with the `Boba` table.
- `bbt_tokens` (int): The number of boba tokens the participant has.

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

The `BobaOrders` table has the following columns:

- `id` (int): The unique identifier for the boba order.
- `participant_id` (int): The ID of the participant, modeling a many-to-one relationship with the `Participant` table.
- `status` (str): The status of the order. Default is "Placed", and can be updated to "In Progress", "Out for Delivery", "Delivered" or "Cancelled".
- `size` (str): The size of the boba. Default is "Medium", and is free text.
- `flavour` (str): The flavour of the boba. Default is "HK Milk Tea", and is free text.
- `sweetness` (str): The sweetness of the boba. Default is "50% Sweet", and is free text.
- `ice` (str): The ice level of the boba. Default is "Regular Ice", and is free text.
- `toppings` (str): The toppings of the boba. Default is "None", and is free text.

## API Endpoints

High level list:

- `GET /users`: Get all users (with optional filters for checked in status and pagination 50 at a time)
- `GET /users/<int:participant_id>`: Get a user by ID
- `PUT /users/<int:participant_id>`: Update a user by ID
- `GET /skills`: Get all skills (with optional filters for frequency, average rating, and keyword)
- `GET /checkin`: Check if a user is checked in
- `POST /checkin`: Check in a user with a volunteer ID
- `POST /register`: Register a new user

😋🧋

- `POST /boba`: Place an order for boba
- `GET /boba`: Get all boba orders, with optional filters for participant_id and status
- `PUT /boba`: Update a boba order status by ID

### `GET /users`

Returns a json dictionary of all users in the database with their IDs as keys.

Optional arguments:

- `checked_in` (bool): Whether to filter the users by checked in status. Default is no filter, accepts `true` or `false`.
- `page` (int): The page number to return, with 50 users per page. Default is no pagination (i.e. all users).

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

Takes the user's ID as a parameter, and a json body with a dictionary of fields to update.

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
- `keyword` (str): A keyword to filter the skills for if they contain the keyword in their name (case-insensitive). Default is no keyword constraint.

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

#### Example Request 2

Get all the skills with "py" in their name.

```
GET /skills?keyword=py
```

#### Example Response 2

The skills that meet the criteria are "PyTorch", "Pygame", "Python", "SciPy" and "Numpy".

```json
{
    "Numpy": {
        "average_rating": 2.45,
        "frequency": 20
    },
    "PyTorch": {
        "average_rating": 2.03,
        "frequency": 33
    },
    "Pygame": {
        "average_rating": 2.58,
        "frequency": 31
    },
    "Python": {
        "average_rating": 3.16,
        "frequency": 51
    },
    "SciPy": {
        "average_rating": 2.44,
        "frequency": 34
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
    "checked_in": false,
    "participant_id": 1
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
    "participant_id": 100,
    "volunteer_id": 1
}
```

### `POST /register`

Registers a new participant, and returns the participant's details if successful.

A participant's data is taken in just like the `PUT /users/<int:participant_id>` endpoint, i.e. a json body with a dictionary of fields to set.

```json
{
    "name": "Eeeeee Aaaaaa",
    "company": "A Ltd",
    "email": "aaaa@example.net",
    "phone": "+1-613-123-4567",
    "skills": [
        {
            "skill": "Python",
            "rating": 4
        },
        {
            "skill": "SQL",
            "rating": 3
        }
    ]
}
```

Note: there is a check for unique emails, so if the email already exists, the request will return a 400 Email Already Exists error. Since registration is rare, a full query is made to check for the email's existence.

#### Example Request

```
POST /register
{
    "name": "Eeeeee Aaaaaa",
    "company": "A Ltd",
    "email": "aaaa@example.net",
    "phone": "+1-613-123-4567",
    "skills": [
        {
            "skill": "Python",
            "rating": 4
        },
        {
            "skill": "SQL",
            "rating": 3
        }
    ]
}
```

#### Example Response

The participant is registered and their details are returned.

```json
{
    "1029": {
        "checked_in": false,
        "company": "A Ltd",
        "email": "aaaa@example.net",
        "name": "Eeeeee Aaaaaa",
        "phone": "+1-613-123-4567",
        "skills": [
            {
                "rating": 4,
                "skill": "Python"
            },
            {
                "rating": 3,
                "skill": "SQL"
            }
        ]
    }
}
```

### `GET /boba`

Returns a json dictionary of all boba orders in the database with their IDs as keys.

Optional arguments:

- `participant_id` (int): The ID of the participant to filter the orders for. Default is no filter.
- `status` (str): The status of the order to filter for. Default is no filter.

#### Example Request

```json
GET /boba
```

#### Example Response

```json
{
    "1": {
        "flavour": "HK Milk Tea",
        "ice": "Regular Ice",
        "participant_id": 1,
        "size": "Medium",
        "status": "Placed",
        "sweetness": "50% Sweet",
        "toppings": "None"
    },
    "2": {
        "flavour": "HK Milk Tea",
        "ice": "Regular Ice",
        "participant_id": 2,
        "size": "Medium",
        "status": "Placed",
        "sweetness": "50% Sweet",
        "toppings": "None"
    }
}
```

### `POST /boba`

Places an order for boba, and returns the order's details.

Takes the participant's ID and a json body with a dictionary of optional fields to set.

```json
{
    "participant_id": 2,
    "size": "Huge",
    "flavour": "Earl Grey",
    "not_a_field": "Mangoes",
    "toppings": "Tapioca"
}
```

Note: there is a check for the participant's existence, so if the participant does not exist, the request will return a 404 error.

#### Example Request

```json
POST /boba
{
    "participant_id": 2,
    "size": "Huge",
    "flavour": "Earl Grey",
    "not_a_field": "Mangoes",
    "toppings": "Tapioca"
}
```

#### Example Response

```json
{
    "5": {
        "flavour": "Earl Grey",
        "ice": "Regular Ice",
        "participant_id": 2,
        "size": "Huge",
        "status": "Placed",
        "sweetness": "50% Sweet",
        "toppings": "Tapioca"
    }
}
```

### `PUT /boba`

Updates a boba order's status by ID, and returns the updated order's details.

Takes a json body with the order's ID and a mandatory `status` field to update. The order must exist, and the status must be one of "In Progress", "Out for Delivery", "Delivered" or "Cancelled", or the request will return a 400 Invalid status.

```json
{
    "status": "In Progress",
    "order_id": 5
}
```

### Example Request

```json
PUT /boba
{
    "status": "In Progress",
    "order_id": 5
}
```

### Example Response

```json
{
    "5": {
        "flavour": "Earl Grey",
        "ice": "Regular Ice",
        "participant_id": 2,
        "size": "Huge",
        "status": "In Progress",
        "sweetness": "50% Sweet",
        "toppings": "Tapioca"
    }
}
```
