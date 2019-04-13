.PHONY: all test clean-test-output
.SILENT: clean-test-output

all: test

test: clean-test-output
	./facturedata/__main__.py --doctest

	./facturedata/__main__.py --conf-dir="tests/examples/json_output" --skip-targets --output-type=json > test_output/json_output/output.json
	diff tests/examples/json_output/expected_output.json test_output/json_output/output.json && echo OK

	cp tests/examples/sql_inject_target/original.sql test_output/sql_inject_target/result.sql
	./facturedata/__main__.py --conf-dir="tests/examples/sql_inject_target" --skip-targets --output-type=json > test_output/sql_inject_target/debug_intermediate.json
	./facturedata/__main__.py --conf-dir="tests/examples/sql_inject_target"
	diff tests/examples/sql_inject_target/expected_result.sql test_output/sql_inject_target/result.sql && echo OK

clean-test-output:
	rm -rf test_output
	mkdir -p test_output/json_output
	mkdir -p test_output/sql_inject_target

release: clean-releases
	python3 setup.py sdist

clean-releases:
	rm -rf dist

publish-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

install-test:
	pip3 install --index-url https://test.pypi.org/simple/ facturedata

publish:
	twine upload dist/*

tag:
	git tag v`grep -o "version.*" setup.py | egrep -o "[0-9.]+"`

tag-push:
	git push origin v`grep -o "version.*" setup.py | egrep -o "[0-9.]+"`
