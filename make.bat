tests:
	coverage run --source hardware setup.py test
	codecov --token=d7078188-16c9-4e86-8d10-2b3c9f1aa992
