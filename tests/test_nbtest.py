import os
from nbtest.nbtest import nbtest

basedir = os.path.abspath(os.path.dirname(__file__))


def test_simple():
    assert nbtest([f'{basedir}/simple/success.ipynb']) == 0
    assert nbtest([f'{basedir}/simple/failure.ipynb']) == 1


def test_setup_teardown():
    assert nbtest([f'{basedir}/setup_teardown/success.ipynb'],
                  setup_notebook=f'{basedir}/setup.ipynb',
                  teardown_notebook=f'{basedir}/teardown.ipynb') == 0
    with open('_global_setup.txt') as f:
        assert f.readline() == "setup: {}\n"
    with open('_setup.txt') as f:
        assert f.readline() == "setup: {'notebook': 'success.ipynb'}\n"
    with open('_setup.success.txt') as f:
        assert f.readline() == "setup: {'notebook': 'success.ipynb'}\n"
    with open('_teardown.success.txt') as f:
        assert f.readline() == "teardown: {'notebook': 'success.ipynb'}\n"
    with open('_teardown.txt') as f:
        assert f.readline() == "teardown: {'notebook': 'success.ipynb'}\n"
    with open('_global_teardown.txt') as f:
        assert f.readline() == "teardown: {}\n"


def test_mocks():
    assert nbtest([f'{basedir}/mocks/success.ipynb'], mocks='tests.mocks') == 0
