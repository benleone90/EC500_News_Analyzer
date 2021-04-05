# EC 500 Project - News Injester Module

The news injester API uses [NewsAPI.org](https://newsapi.org/) to create custom endpoints.

## API Endpoints
- `/news/everything/<text>`
    - Returns JSON with all information and meta-data regarding the query in the \<text> field.

## Notes

- Main apps are named `application.py` to conform to Amazon Elastic Beanstalk requirements.
