from docIngester.src import fileuploader as fu
from nlp import nlpanalyzer as nlp
from newsfeed import newsfeedingester as nfi
import json
import queue
import threading


def searchHelper(doc, keywords, finishQ):
    ret = dict()
    title = doc.get("Name")  # Extract doc name
    text = doc.get('Text').get('Text')  # Extract all paragraphs in doc
    ret["Title"] = title  # Store Title
    ret["Paragraphs"] = []

    # Go through text and extract all entities
    for i, paragraph in enumerate(text):
        entities = set(nlp.analyze_entity(paragraph))  # Extract entities from each paragraph
        intersection = keywords & entities  # Find if any entities match our keywords (using set intersection)
        if len(intersection) != 0:  # If matches are found, add to list of paragraphs
            ret["Paragraphs"].append((i + 1, paragraph))

    if not ret["Paragraphs"]:  # If No matches are found, don't modify the Queue
        return
    else:
        finishQ.put(ret)  # Otherwise add the item to the Queue


def search(username, *args):
    ret = []  # initialize return list

    if args is None or args == '':
        return ret

    startq = queue.Queue()  # Start queue where we put our tasks to complete
    finishqueue = queue.Queue()  # Final Queue where results are placed

    keywords = set(args)  # Place keywords in a set for fast lookup

    docs, code = fu.read_many(username)  # Extract all documents belonging to user

    if docs is None:
        return ret

    # Place documents in a Queue so we can use multiple threads
    for doc in docs:
        startq.put(doc)

    # Create threads to run tasks in parallel
    threads = []
    for i in range(len(docs)):
        t = threading.Thread(target=searchHelper, args=(startq.get(), keywords, finishqueue))
        threads.append(t)

    # Start Threads
    for thread in threads:
        thread.start()

    # Join Threads
    for thread in threads:
        thread.join()

    # Extract items from Queue and add to return list
    while not finishqueue.empty():
        ret.append(finishqueue.get())

    return ret
