# Kama Career Backend Service

## Overview

This project scrapes LinkedIn job postings and stores them in DynamoDB using AWS Lambda. It uses the serverless.yml configuration to define the Lambda function and schedule the scraping tasks.

## Tech Stack

- Python
- AWS Lambda
- Serverless Framework
- DynamoDB

## Getting Started

### Prerequisites

- Python 3.9+
- AWS account (for Lambda & DynamoDB)
- Serverless CLI
- Poetry (Python package manager)

### Installation and Local Run

1. Clone the repository
2. Install dependencies:

```bash
poetry install
```

3. Activate the virtual environment:

```bash
poetry shell
```

4. Run the scraper locally:

```bash
poetry run python scraper.py
```

## Deployment

### Local Deployment

To deploy to your local environment:

```bash
npm run deploy:local
```

### Production Deployment

To deploy to production:

```bash
npm run deploy:prod
```

This reads `serverless.yml` and creates the Lambda function with a scheduled event to scrape LinkedIn job postings.

## Code Structure

- **LinkedInJobParser**: Parses job posting HTML
- **scraper.py**: Main scraping workflow, including scheduling
- **Job**: Defines job data structure
- **JobStore**: Stores data in DynamoDB

## Contributing

Feel free to open an issue or create a pull request.

## Run locally

```bash
fastapi dev src/main.py --app app
```
