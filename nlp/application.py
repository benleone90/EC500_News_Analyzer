from flask import Flask, request
from google.cloud import language_v1

application = Flask(__name__)
client = language_v1.LanguageServiceClient()


@application.route('/nlp/score/<text>')
def analyzeScore(text=None):
    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_sentiment(
        request={'document': document}).document_sentiment
    return response.score


@application.route('/nlp/magnitude/<text>')
def analyzeMagnitude(text=None):
    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_sentiment(
        request={'document': document}).document_sentiment
    return response.magnitude


@application.route('/nlp/entities/<text>')
def analyzeEntities(text=None):
    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_entities(
        request={'document': document, 'encoding_type': language_v1.EncodingType.UTF8})
    for entity in response.entities:
        return {'name': entity.name, 'salience': entity.salience, 'type': language_v1.Entity.Type(entity.type_).name}


if __name__ == '__main__':
    application.run(debug=True)
