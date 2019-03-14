.PHONY: all test clean-test-output
.SILENT: clean-test-output

all: test

test: clean-test-output
	./facture.py --doctest

	./facture.py --conf-dir="tests/examples/json_output" --skip-targets --output-type=json > test_output/json_output/output.json
	diff tests/examples/json_output/expected_output.json test_output/json_output/output.json && echo OK

	cp tests/examples/sql_inject_target/original.sql test_output/sql_inject_target/result.sql
	./facture.py --conf-dir="tests/examples/sql_inject_target"
	# diff tests/examples/sql_inject_target/expected_result.sql test_output/sql_inject_target/result.sql && echo OK

clean-test-output:
	rm -rf test_output
	mkdir -p test_output/json_output
	mkdir -p test_output/sql_inject_target
