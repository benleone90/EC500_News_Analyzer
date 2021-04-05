# EC 500 Project - Natural Language Processing (NLP) Module

The NLP module uses the Google NLP Analysis to provide an API endpoint for the final News Analysis project

## API Endpoints

- `/nlp/score/<text>`
  - Returns the score for how positive or negative is the sentiment of the \<text>.
- `/nlp/magnitude/<text>`
  - Reutrns the magnitue for cases with multiple sentences to show what the magnitue or impact a sentence has on overall sentiment.
- `/nlp/entities/<text>`
  - Returns the entity type: PERSON, LOCATION, ADDRESS, NUMBER, et al and salience score from [0.0, 1.0]

## Notes

- Main apps are named `application.py` to conform to Amazon Elastic Beanstalk requirements.
