from docIngester.src import fileuploader as fu
from nlp.src import nlpanalyzer as nlp
import json

# Report Generator will run NLP on document
def generateReport(name, document):
    document_json = json.dumps({"Name": document})
    doc, msg, code = fu.read_one(name, document_json)
    if doc is None:
        return None
    # print(doc)
    text = doc.get('Text').get('Text')  # Extract All paragraphs from text
    nlpresults = []  # Array of results

    # Perform sentiment and entity:sentiment analysis on each paragraph
    for paragraph in text:
        sentiment = nlp.analyze_sentiment(paragraph)
        entity_sent = nlp.analyze_entity_sentiment(paragraph)
        nlpresults.append((sentiment, entity_sent))

    return nlpresults

