from docIngester.src import fileuploader as fu
from nlp import nlpanalyzer as nlp
from newsfeed import newsfeedingester as nfi
import json
from heapq import nlargest


# Report Generator
# Compiles a dictionary of the following fields
#   - OVERALL_SENTIMENT : A (float) score indicating the overall sentiment of the document
#   - MOST_POSITIVE_PAR: A tuple consisting of: the score of the most positive paragraph in the document and
#                        the associated text
#   - LEAST_POSITIVE_PAR: A tuple consisting of: the score of the least positive paragraph in the document and
#                         the associated text
#   - ENT_LIST: A list of tuples containing the top 5 most mentioned entities and associated number of paragraphs in
#               which they are mentioned
#   - CONTENT_CLASS: A list of dictionaries including content classification categories for the text overall (sorted
#                    by confidence)
#   - NEWS_LINKS: A dictionary of dictionaries with each of the top 5 entities as a key in the top-level dictionary and
#                 a list of dictionaries of articles (with keys "Summary" and "URL" in the text level)
#   - PARAGRAPH_BREAKDOWN: A list of dictionaries with the following information for each paragraph:
#       -NUM: (paragraph number indexed from 1),
#       -TEXT: full text in the paragraph
#       -ENT: List of Entities extracted from the paragraph extracted
#       -SCORE: The sentiment score of this paragraph
def generateReport(uname, document):
    ret = dict()  # Dictionary to return
    document_json = json.dumps({"Name": document})
    doc, code = fu.read_one(uname, document_json)  # Retrieves document from the DB
    if doc is None:
        return None

    text = doc.get('Text').get('Text')  # Extract All paragraphs from text
    fulltext = ' '.join(str(x) for x in text)  # Full document text

    _getParagraphNLPResults(textArray=text, ret=ret)  # Extracts NLP results by paragraph and adds to ret

    _getFullTextContentClass(fulltext=fulltext, ret=ret)  # Extracts Content classification and adds to ret

    _getNewsLinks(ret=ret)  # Get News Links related to top 5 entities - very slow, maybe make optional

    return ret


# Performs Sentiment Analysis and Entity Extraction on each paragraph. Adds the following fields to the return
# dictionary: OVERALL_SENTIMENT, MOST_POSITIVE_PAR, LEAST_POSITIVE_PAR, PARAGRAPH_BREAKDOWN
def _getParagraphNLPResults(textArray, ret):
    nlpresults = []  # Array of results
    entities = dict()  # Dictionary of all entities extracted

    most_pos_par = ""
    most_pos_score = -9999
    most_neg_par = ""
    most_neg_score = 9999
    total_score = 0

    # Perform sentiment and entity:sentiment analysis on each paragraph
    for i, paragraph in enumerate(textArray):

        # Add NLP results to dictionary
        paragraph_dict = dict()
        paragraph_dict["NUM"] = i + 1
        paragraph_dict["TEXT"] = paragraph
        paragraph_dict["ENT"] = nlp.analyze_entity(paragraph)
        paragraph_dict["SCORE"] = nlp.analyze_sentiment(paragraph)
        nlpresults.append(paragraph_dict)

        # Get the entities from the paragraph and update counts
        par_entities = paragraph_dict.get("ENT")
        for entity in par_entities:
            if entities.get(entity) is not None:
                entities[entity] += 1
            else:
                entities[entity] = 1

        # Update most positive and most negative scores/paragraphs
        score = paragraph_dict.get("SCORE")
        total_score += score
        if score > most_pos_score:
            most_pos_score = score
            most_pos_par = paragraph
        if score < most_neg_score:
            most_neg_score = score
            most_neg_par = paragraph


    # Parse the entities dictionary to get the 5 most mentioned entities
    FiveHighest= nlargest(5, entities, key=entities.get)
    ret_entities = list()
    for val in FiveHighest:
        ret_entities.append((val, entities.get(val)))


    # Add items to ret
    ret["OVERALL_SENTIMENT"] = total_score / len(textArray)  # Average sentiment across all paragraphs
    ret["MOST_POSITIVE_PAR"] = (most_pos_score, most_pos_par)  # Add most positive paragraph score and text
    ret["LEAST_POSITIVE_PAR"] = (most_neg_score, most_neg_par)  # Add least positive paragraph score and text
    ret["ENT_LIST"] = ret_entities  # List of Top 5 entities along with associated # mentions
    ret["PARAGRAPH_BREAKDOWN"] = nlpresults  # Paragraph by Paragraph Breakdown


# Extracts a list of content categories and sorts by associated confidence score (largest score first)
def _getFullTextContentClass(fulltext, ret):
    content = nlp.classify_content(fulltext)  # Extract content categories
    if content:
        content.sort(key=lambda x: (x.get("Score")), reverse=True)  # Sort content classes by score

    ret["CONTENT_CLASS"] = content

# Extract news articles related to the top 5 entities -- very slow, maybe make an option
def _getNewsLinks(ret):
    mydict = dict()
    ents = ret.get("ENT_LIST")
    for entity in ents:
        query = entity[0]
        results = nfi.keyword_query([query])
        mydict[query] = results

    ret["NEWS_LINKS"] = mydict






