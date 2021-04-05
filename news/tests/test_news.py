from news.application import news
import pytest
import requests
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


def test_everything():
    response = news("Bitcoin")
    assert type(response) is dict
