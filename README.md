# GraphQL Server

A GraphQL server built with [Ariadne](https://ariadnegraphql.org/) and served as an ASGI app. User data is loaded from a CSV file (`users.csv`) containing 210+ records spanning 40+ countries.

## Setup

```bash
bash scripts/setup.sh
```

## Running

```bash
bash scripts/start.sh
```

The server starts at `http://localhost:4001`. Visit that URL in a browser for the interactive GraphQL Playground.

---

## Data

`users.csv` contains 210 users with the following fields:

| Field        | Description                     |
|--------------|---------------------------------|
| `id`         | Unique numeric ID               |
| `name`       | Full name                       |
| `email`      | Email address                   |
| `address`    | Street address                  |
| `city`       | City                            |
| `state`      | State / province / region       |
| `country`    | Country                         |
| `age`        | Age (integer)                   |
| `phone`      | Phone number                    |
| `occupation` | Job title / occupation          |
| `zip_code`   | Postal / ZIP code               |

---

## Schema

```graphql
type Query {
  hello(name: String): String!

  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!

  usersByCity(city: String!): [User!]!
  usersByState(state: String!): [User!]!
  usersByCountry(country: String!): [User!]!
  usersByAgeRange(min: Int!, max: Int!): [User!]!
  usersByOccupation(occupation: String!): [User!]!

  searchUsers(query: String!): [User!]!

  countries: [String!]!
  cities: [String!]!
  occupations: [String!]!

  stats: Stats!
}

type User {
  id: ID!
  name: String!
  email: String!
  address: String!
  city: String!
  state: String!
  country: String!
  age: Int!
  phone: String!
  occupation: String!
  zip_code: String!
}

type Stats {
  totalUsers: Int!
  averageAge: Float!
  oldestUser: User
  youngestUser: User
  countriesCount: Int!
  citiesCount: Int!
  occupationsCount: Int!
  ageDistribution: [AgeBucket!]!
}

type AgeBucket {
  range: String!
  count: Int!
}
```

---

## Queries

### `hello`

Returns a greeting string.

**Arguments**

| Argument | Type     | Required | Description                         |
|----------|----------|----------|-------------------------------------|
| `name`   | `String` | No       | Name to greet (defaults to "World") |

```graphql
query {
  hello(name: "Alice")
}
```

---

### `user`

Fetch a single user by ID.

| Argument | Type  | Required | Description   |
|----------|-------|----------|---------------|
| `id`     | `ID!` | Yes      | The user's ID |

```graphql
query {
  user(id: "42") {
    id
    name
    email
    city
    country
    occupation
    age
  }
}
```

---

### `users`

Fetch all users, with optional pagination.

| Argument | Type  | Required | Description                      |
|----------|-------|----------|----------------------------------|
| `limit`  | `Int` | No       | Max number of users to return    |
| `offset` | `Int` | No       | Number of users to skip (default 0) |

```graphql
query {
  users(limit: 10, offset: 0) {
    id
    name
    city
    country
    age
  }
}
```

---

### `usersByCity`

Fetch all users in a given city (case-insensitive).

```graphql
query {
  usersByCity(city: "Berlin") {
    id
    name
    occupation
    age
  }
}
```

---

### `usersByState`

Fetch all users in a given state or province (case-insensitive).

```graphql
query {
  usersByState(state: "California") {
    id
    name
    city
    age
  }
}
```

---

### `usersByCountry`

Fetch all users from a given country (case-insensitive).

```graphql
query {
  usersByCountry(country: "India") {
    id
    name
    city
    occupation
    age
  }
}
```

---

### `usersByAgeRange`

Fetch users whose age falls within `[min, max]`.

| Argument | Type   | Required | Description       |
|----------|--------|----------|-------------------|
| `min`    | `Int!` | Yes      | Minimum age       |
| `max`    | `Int!` | Yes      | Maximum age       |

```graphql
query {
  usersByAgeRange(min: 25, max: 35) {
    id
    name
    age
    country
  }
}
```

---

### `usersByOccupation`

Fetch users with a specific occupation (case-insensitive exact match).

```graphql
query {
  usersByOccupation(occupation: "Software Engineer") {
    id
    name
    city
    country
  }
}
```

---

### `searchUsers`

Full-text search across `name`, `email`, `city`, `country`, and `occupation` fields.

| Argument | Type      | Required | Description        |
|----------|-----------|----------|--------------------|
| `query`  | `String!` | Yes      | Search term        |

```graphql
query {
  searchUsers(query: "engineer") {
    id
    name
    occupation
    city
    country
  }
}
```

---

### `countries`

Returns a sorted list of all distinct countries in the dataset.

```graphql
query {
  countries
}
```

---

### `cities`

Returns a sorted list of all distinct cities in the dataset.

```graphql
query {
  cities
}
```

---

### `occupations`

Returns a sorted list of all distinct occupations in the dataset.

```graphql
query {
  occupations
}
```

---

### `stats`

Returns aggregate statistics about the dataset.

```graphql
query {
  stats {
    totalUsers
    averageAge
    countriesCount
    citiesCount
    occupationsCount
    oldestUser  { name age country }
    youngestUser { name age country }
    ageDistribution {
      range
      count
    }
  }
}
```

**Example response**

```json
{
  "data": {
    "stats": {
      "totalUsers": 210,
      "averageAge": 33.8,
      "countriesCount": 42,
      "citiesCount": 175,
      "occupationsCount": 98,
      "oldestUser":   { "name": "Steve Evans",  "age": 61, "country": "USA" },
      "youngestUser": { "name": "Bella Young",  "age": 21, "country": "USA" },
      "ageDistribution": [
        { "range": "18-25", "count": 18 },
        { "range": "26-35", "count": 89 },
        { "range": "36-45", "count": 72 },
        { "range": "46-55", "count": 24 },
        { "range": "56+",   "count": 7  }
      ]
    }
  }
}
```
