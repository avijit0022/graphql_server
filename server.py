import csv
import logging
import os

from ariadne import QueryType, make_executable_schema
from ariadne.asgi import GraphQL

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("graphql_server")

# --- Load data from CSV ---
CSV_PATH = os.path.join(os.path.dirname(__file__), "users.csv")

def load_users():
    users = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["age"] = int(row["age"])
            users.append(row)
    logger.info("Loaded %d users from %s", len(users), CSV_PATH)
    return users

USERS = load_users()

# --- Schema definition ---
type_defs = """
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
"""

# --- Resolvers ---
query = QueryType()

@query.field("hello")
def resolve_hello(_, info, name=None):
    logger.info("hello query called with name=%s", name)
    return f"Hello, {name or 'World'}!"

@query.field("user")
def resolve_user(_, info, id):
    logger.info("user query: id=%s", id)
    user = next((u for u in USERS if u["id"] == id), None)
    if not user:
        logger.warning("user not found: id=%s", id)
    return user

@query.field("users")
def resolve_users(_, info, limit=None, offset=0):
    logger.info("users query: limit=%s offset=%s", limit, offset)
    result = USERS[offset:]
    if limit is not None:
        result = result[:limit]
    return result

@query.field("usersByCity")
def resolve_users_by_city(_, info, city):
    logger.info("usersByCity query: city=%s", city)
    return [u for u in USERS if u["city"].lower() == city.lower()]

@query.field("usersByState")
def resolve_users_by_state(_, info, state):
    logger.info("usersByState query: state=%s", state)
    return [u for u in USERS if u["state"].lower() == state.lower()]

@query.field("usersByCountry")
def resolve_users_by_country(_, info, country):
    logger.info("usersByCountry query: country=%s", country)
    return [u for u in USERS if u["country"].lower() == country.lower()]

@query.field("usersByAgeRange")
def resolve_users_by_age_range(_, info, min, max):
    logger.info("usersByAgeRange query: min=%d max=%d", min, max)
    return [u for u in USERS if min <= u["age"] <= max]

@query.field("usersByOccupation")
def resolve_users_by_occupation(_, info, occupation):
    logger.info("usersByOccupation query: occupation=%s", occupation)
    return [u for u in USERS if u["occupation"].lower() == occupation.lower()]

@query.field("searchUsers")
def resolve_search_users(_, info, query):
    logger.info("searchUsers query: query=%s", query)
    q = query.lower()
    return [
        u for u in USERS
        if q in u["name"].lower()
        or q in u["email"].lower()
        or q in u["city"].lower()
        or q in u["country"].lower()
        or q in u["occupation"].lower()
    ]

@query.field("countries")
def resolve_countries(_, info):
    return sorted(set(u["country"] for u in USERS))

@query.field("cities")
def resolve_cities(_, info):
    return sorted(set(u["city"] for u in USERS))

@query.field("occupations")
def resolve_occupations(_, info):
    return sorted(set(u["occupation"] for u in USERS))

@query.field("stats")
def resolve_stats(_, info):
    ages = [u["age"] for u in USERS]
    buckets = [
        ("18-25", 18, 25),
        ("26-35", 26, 35),
        ("36-45", 36, 45),
        ("46-55", 46, 55),
        ("56+",   56, 999),
    ]
    age_distribution = [
        {"range": label, "count": sum(1 for a in ages if lo <= a <= hi)}
        for label, lo, hi in buckets
    ]
    return {
        "totalUsers": len(USERS),
        "averageAge": round(sum(ages) / len(ages), 2),
        "oldestUser": max(USERS, key=lambda u: u["age"]),
        "youngestUser": min(USERS, key=lambda u: u["age"]),
        "countriesCount": len(set(u["country"] for u in USERS)),
        "citiesCount": len(set(u["city"] for u in USERS)),
        "occupationsCount": len(set(u["occupation"] for u in USERS)),
        "ageDistribution": age_distribution,
    }

# --- App ---
logger.info("Building GraphQL schema")
schema = make_executable_schema(type_defs, query)
app = GraphQL(schema, debug=True)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("GRAPHQL_SERVER_HOST", "localhost")
    port = int(os.getenv("GRAPHQL_SERVER_PORT", "4001"))
    logger.info("Starting GraphQL server on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port)
