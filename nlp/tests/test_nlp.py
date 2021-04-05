from nlp.application import *
import pytest
import requests
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


def test_score():
    response = analyzeScore("Hello World")
    assert type(response) is float


def test_magnitude():
    response = analyzeMagnitude("Hello World!")
    assert type(response) is float


def test_entities():
    response = analyzeEntities("Hello World! My name is Ben.")
    assert type(response) is dict
