# Hack the North 2024 Backend Challenge

From: https://gist.github.com/DanielYu842/ac519f42477cbf7ec7871321bd0b900e#file-htn-backend-challenge-2024-md 

## Introduction
On the Backend Team at Hack the North, you'll be responsible for helping us build and maintain the important applications and internal tools that help make our event work. In previous years, this has included Discord Bots, a QR Code Scanner, a system for our mobile apps, and internal analytics/payment tools. Additionally, we also maintain HackerAPI, the service that powers our backend. 

This small challenge will help us determine how you work, including your ability to be resourceful, and how you think about your work.

Please email backend-leads@hackthenorth.com if you have any questions.

## Alternate Project Submission
If you believe you have an existing project that demonstrates the same skills and competencies as this challenge, you may submit that instead of completing this backend challenge. If you choose to do so, we will use your project to check for the same skills and competencies that we expect most applicants to demonstrate when completing the backend challenge. However, we understand that an existing project will not be exactly the same as this backend challenge so the rough criteria that we would use to evaluate an existing project is as follows:

- Demonstrates the ability to utilize SQL queries that are more complex than simple SELECTs (either raw SQL queries or through an ORM)
- Understanding of different SQL table relationships
- Overall design and implementation, specifically with respect to code quality and architecture
- Knowledgeable with various API design principles (GraphQL or REST principles)

Note that the project you submit should be done **entirely** by yourself!

## Challenge
You've just created a new hackathon series and it's wildly successful! However, the number of applications is quickly becoming too much for your Excel spreadsheet. The goal is to develop a basic GraphQL or REST API server to store and work with your hackathon participants' data. Please remember to document your API within your repository's README!

### Data
We have 1,000+ fake user profiles at [here](https://gist.github.com/DanielYu842/607c1ae9c63c4e83e38865797057ff8f). The JSON schema is:

```json
{
  "name": <string>,
  "company": <string>,
  "email": <string>,
  "phone": <string>,
  "skills": [
    {
      "skill": <string>,
      "rating": <int>
    }
  ]
}
```

### Database
You can either download the user data from the link above and use the local JSON file, or make an HTTP request when running the program that inserts the data to a database.

For simplicity, we recommend using SQLite for the database as it is the easiest to setup and likely already exists on your computer. However, if you are more familiar with other databases, e.g. PostgreSQL, feel free to use them!

We are particularly interested in seeing how you define your database table(s) and partition the data appropriately.

### Frameworks and Languages

You may use any language with any framework of your choice for creating a backend server capable for handling requests e.g. Python/Flask, Node/Express, etc. We have provided boilerplate code for Express with Node.js for GraphQL or REST APIs (see Docker files below).

Please note that **using a particular language/framework will not penalize you in any way** - feel free to use whichever technologies you are most comfortable with or want to learn more about! Similarly, **we will not penalize you for choosing to use GraphQL or REST API principles** - both are completely acceptable!

Your backend server should serve as a quick interface to the database. The key requirement is to allow us to see the user data in a JSON format, through a GraphQL or REST API.

#### Potential Boilerplate

Below, we have provided Dockerfiles and associated project files for different options. Please note, **you do not have to use any of these files** - feel free to use your own setup! Additionally, please do not consider these to be exemplary methods of structuring your project - they are simply provided to help you get up and running as quickly as possible. You may modify project structure in any way you wish, including adding any libraries/frameworks.

[Boilerplate](https://drive.google.com/drive/folders/1g0ZoneE2yk2pD0J-Dhf33bN6mRgF4A6G?usp=sharing)

### API

At the minimum, this is what it should have:

#### All Users Endpoint
This endpoint should return a list of all user data from the database in a JSON format.

_Example GraphQL (feel free to change format):_
```
query {
  users {
    name
    email
    skills {
      name
      rating
    }
    ...
  }
}
```

_Example REST:_ 

`GET localhost:3000/users/` or similar

#### User Information Endpoint
This endpoint should return the user data for a specific user. Depending on your database schema, it is up to you to decide what identifies a single user and design an endpoint that will give the full details about that user.

_Example GraphQL (feel free to change format):_
```
query {
  user(INSERT_IDENTIFIER: FOO) {
    name
    email
    skills {
      name
      rating
    }
    ...
  }
}
```

_Example REST:_

`GET localhost:3000/users/123` or similar

#### Updating User Data Endpoint
This endpoint should allow you to update a given user's data by accepting data in a JSON format and return the updated user data as the response. The important design consideration for this endpoint is that it must support partial updating. This will either be a new mutation (GraphQL) or a PUT only method to the same URL as the user information endpoint above (REST).

_Example GraphQL (feel free to change format):_
```
query {
  updateUser(INSERT_IDENTIFIER: FOO, data: {phone: "+1 (555) 123 4567"}) {
    name
    phone
    ...
  }
}
```

_Example REST:_

Submitting the following JSON:

```json
  {
    "phone": "+1 (555) 123 4567"
  }
```

to the given URL: `PUT localhost:3000/users/123` or similar 

should update their phone number to `+1 (555) 123 4567` and return the full user data with the new phone number.

Note: If a user has new skills, these skills should be added to the database. Any existing skills should have their ratings updated.

#### Skills Endpoints
These endpoint should show a list of skills and aggregate info about them. Note that in the context of your hackathon, users do not gain/lose skills very often.

Try to implement the following (in SQL or with an ORM):
- Number of users with each skill (frequency)
- Query parameter filtering - minimum/maximum frequency

_Example GraphQL (feel free to change format):_
```
query {
  skills(data: {min_frequency: 5, max_frequency: 10}) {
    name
    frequency
  }
}
```

_Example REST:_

`GET localhost:3000/skills/?min_frequency=5&max_frequency=10` or similar

### Notes
- You may have two separate applications if you'd like.
  - You can include a script to create the appropriate database tables and insert the default data.
  - The second application can assume that the database already exists and launch the app to start listening for requests.
- You are free to use any existing library or dependency for the language of your choice (don't forget to document).
- You can reference any online resources or documentation, however, please do not plagiarize.

### Bonus

If you've implemented the basic requirements quickly, feel free to make improvements as you see fit, especially if the improvements you implement are part of a larger vision for your application as a product for hackathon attendees. You may also outline any improvements you'd make in your README. Here are some potential ideas:

- At Hack the North, we use a QR scanner tool that scans hacker badges every time they go to a workshop, participate in an activity, or get food. Generate some mock data to show scan events and/or create an endpoint to "scan" a user for an event. Create an endpoint that returns all the events that a user was scanned for.

- Hardware projects at Hack the North have become more popular over the years — during the event, hackers can borrow hardware from us for their projects. Create a set of endpoints to allow users to sign out and return hardware.

- One of the first things we do during the event is register attendees when they arrive. Create a set of endpoints for volunteers to check users into the event.

- What sort of information might be useful to a specific hacker during the event? Create an endpoint that provides it.

- Write some tests. Feel free to use any testing framework, but make sure to document how we can run your tests!

- Deploy your application. We use Google Cloud (GKE) here at Hack the North, but feel free to self-host or use any cloud provider of your choice.

Note that these bonus tasks are not a comprehensive list, just a small set of ideas. Feel free to implement all or some of them, or envision new changes. Be creative! We're excited to see what you come up with! Whatever you add, make sure to document it!

__Please submit your entry by uploading it to a Github Repository and submitting the link to this [form](https://forms.gle/b3bFks6AZUVj7nLK7) (make sure it is accessible to us). Remember to provide documentation in the README! If you are not able to complete all components of the challenge - don't worry & please submit your challenge anyhow, we'd love to take a look! Just make sure to document what you've completed! Good luck! :)__