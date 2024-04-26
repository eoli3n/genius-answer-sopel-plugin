```bash
$ pip install build twine
# check version on pypi
$ git tag 0.x.x
$ python -m build
$ twine check dist/*
$ twine upload dist/*
