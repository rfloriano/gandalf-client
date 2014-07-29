# This file is part of gandalf-client.
# https://github.com/rfloriano/gandalf-client

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com
#

# lists all available targets
list:
	@sh -c "$(MAKE) -p no_targets__ | awk -F':' '/^[a-zA-Z0-9][^\$$#\/\\t=]*:([^=]|$$)/ {split(\$$1,A,/ /);for(i in A)print A[i]}' | grep -v '__\$$' | grep -v 'make\[1\]' | grep -v 'Makefile' | sort"
# required for list
no_targets__:

# install all dependencies (do not forget to create a virtualenv first)
setup:
	@pip install -U -e .\[tests\]

# test your application (tests in the tests/ directory)
test: services_test unit doctest

services_test: mongo_test gandalf_test

doctest:
	@cd docs && make doctest

unit:
	@coverage run --branch `which nosetests` -vv --with-yanc -s tests/
	@coverage report -m --fail-under=80

focus:
	@coverage run --branch `which nosetests` -vv --with-yanc --logging-level=WARNING --with-focus -s tests/

# show coverage in html format
coverage-html: unit
	@coverage html -d cover


# get a mongodb instance up (localhost:3333)
mongo: kill_mongo
	@mkdir -p /tmp/gandalf-client/mongodata && mongod --dbpath /tmp/gandalf-client/mongodata --logpath /tmp/gandalf-client/mongolog --port 3333 --quiet &

# kill this mongodb instance (localhost:3333)
kill_mongo:
	@-ps aux | egrep -i 'mongod.+3333' | egrep -v egrep | awk '{ print $$2 }' | xargs kill -9

# clear all data in this mongodb instance (localhost: 3333)
clear_mongo:
	@rm -rf /tmp/gandalf-client && mkdir -p /tmp/gandalf-client/mongodata

# get a mongodb instance up for your unit tests (localhost:3334)
mongo_test: kill_mongo_test
	@mkdir -p /tmp/gandalf-client/
	@rm -rf /tmp/gandalf-client/mongotestdata && mkdir -p /tmp/gandalf-client/mongotestdata
	@mongod --dbpath /tmp/gandalf-client/mongotestdata --logpath /tmp/gandalf-client/mongotestlog --port 3334 --quiet --fork
	@echo 'waiting for mongo...'
	@until mongo --port 3334 --eval "quit()"; do sleep 0.25; done > /dev/null 2> /dev/null

# kill the test mongodb instance (localhost: 3334)
kill_mongo_test:
	@-ps aux | egrep -i 'mongod.+3334' | egrep -v egrep | awk '{ print $$2 }' | xargs kill -9

# get a gandalft instance up for your unit tests (localhost:8001)
gandalf_test: kill_gandalf_test
	@mkdir -p /tmp/git/bare-template/hooks && touch /tmp/git/bare-template/hooks/{post-receive,pre-receive,update}
	@gandalf-server -config="./tests/gandalf-test.conf" &

# kill the test gandalft instance (localhost: 8001)
kill_gandalf_test:
	@-ps aux | egrep -i 'gandalf-server.+-test' | egrep -v egrep | awk '{ print $$2 }' | xargs kill -9

# run tests against all supported python versions
tox:
	@tox

clean-docs:
	@cd docs && make clean

update-docs:
	@cd docs && make html && open _build/html/index.html
