
# Cour de Cassation Data Collection and API

This project consists of two parts:
1. **Data collection script** that scrapes, processes, and stores decisions from the Cour de Cassation website into a MongoDB database.
2. **REST API** that exposes the decisions stored in the database for retrieval and searching.

## Table of Contents

- [Project Overview](#project-overview)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Running the Project](#running-the-project)
  - [Running the Data Collection Script](#running-the-data-collection-script)
  - [Running the API](#running-the-api)
- [API Endpoints](#api-endpoints)
  - [Login](#login)
  - [List Decisions](#list-decisions)
  - [Filter by Formation](#filter-by-formation)
  - [Get Decision by ID](#get-decision-by-id)
  - [Search in Content](#search-in-content)
- [Environment Variables](#environment-variables)
- [Docker Setup](#docker-setup)

## Project Overview

### 1. Data Collection Script (`one_shot_webscrape_cass.py`)
This script scrapes `.xml` files from the Cour de Cassation's open data page, extracts decision metadata, and stores it into a MongoDB collection. It collects information such as:
- `TITRE` (Title)
- `FORMATION` (Formation/Division)
- `ID` (Decision ID)
- `CONTENU` (Decision Content)

The data is then stored in the `decisions` collection in MongoDB.

### 2. REST API (`api.py`)
The REST API exposes the collected decisions, allowing users to:
- Retrieve all decisions (title and ID).
- Filter decisions by formation.
- Retrieve a specific decision by ID.
- Search for decisions by matching content against a search query.

Authentication is required for all API endpoints. Authentication uses JSON Web Tokens (JWT).

## Technologies Used

- **Flask** for building the REST API
- **Flask-JWT-Extended** for authentication
- **MongoDB** for storing the data
- **BeautifulSoup** and **Requests** for web scraping
- **Docker** for containerization

## Installation

To set up the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/lehanineraouf/cassation-data-api.git
   cd cassation-data-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in a `.env` file:
   ```bash
   MONGO_URI=mongodb://localhost:27017
   JWT_SECRET_KEY=your_jwt_secret
   API_USERNAME=admin
   API_PASSWORD=your_password
   ```

## Running the Project

### Running the Data Collection Script

To scrape, process, and store the decisions from the Cour de Cassation website, run:

```bash
python one_shot_webscrape_cass.py
```

The script will:
1. Download `.tar.gz` archives of decision `.xml` files.
2. Parse the XML to extract metadata and content.
3. Insert the processed data into MongoDB.

### Running the API

After the data collection script completes, start the API by running:

```bash
python api.py
```

The API will be available at `http://localhost:5000`.

## API Endpoints

### Authentication
All API endpoints are protected by JWT authentication. To interact with the API, you need to:
1. **Log in** to obtain a token.
2. Include the token in the `Authorization` header of each request.

#### Example:
**Login Request:**

```bash
curl -X POST http://localhost:5000/login \
-H "Content-Type: application/json" \
-d '{"username": "admin", "password": "your_password"}'
```

**Login Response:**

```json
{
  "access_token": "your_jwt_token"
}
```

### Endpoints

#### 1. List All Decisions

**GET** `/decisions`

Returns a list of all decisions (ID and title only).

**Request:**

```bash
curl -X GET http://localhost:5000/decisions \
-H "Authorization: Bearer your_jwt_token"
```

#### 2. Filter by Formation

**GET** `/decisions/formation?formation=<formation>`

Filters decisions by their formation.

**Request:**

```bash
curl -X GET "http://localhost:5000/decisions/formation?formation=CIV" \
-H "Authorization: Bearer your_jwt_token"
```

#### 3. Get Decision by ID

**GET** `/decisions/<decision_id>`

Returns the decision's ID, title, and content.

**Request:**

```bash
curl -X GET http://localhost:5000/decisions/<decision_id> \
-H "Authorization: Bearer your_jwt_token"
```

#### 4. Search in Content

**GET** `/search?query=<search_string>`

Returns the top 10 decisions whose content matches the search string.

**Request:**

```bash
curl -X GET "http://localhost:5000/search?query=your_search_query" \
-H "Authorization: Bearer your_jwt_token"
```

## Environment Variables

Create a `.env` file in the project directory with the following variables:

```bash
MONGO_URI=mongodb://mongo:27017
JWT_SECRET_KEY=your_jwt_secret
API_USERNAME=admin
API_PASSWORD=your_password
```

## Docker Setup

You can run the entire project (both data collection and API) using Docker.

1. **Build and start the services** using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. **Data Collection Script** will automatically run when the container is created. It will scrape and store the decisions in the MongoDB database.

3. **API** will be available at `http://localhost:5000`.

## Testing

To test the API:
1. Run the data collection script using `docker-compose`.
2. Obtain a JWT token from the `/login` endpoint.
3. Use the token to make requests to the other endpoints.
