.PHONY: all test clean-test-output
.SILENT: clean-test-output

all: test

test: clean-test-output
	./facture.py --doctest

	./facture.py --conf-dir="tests/examples/example1" --output-type=json > test_output/example1/output.json
	diff tests/examples/example1/expected_output.json test_output/example1/output.json && echo OK

	cp tests/examples/sql_output_injected_into_file/original.sql test_output/sql_output_injected_into_file/under_test.sql
	./facture.py --conf-dir="tests/examples/sql_output_injected_into_file"
	diff tests/examples/sql_output_injected_into_file/expected_result.sql test_output/sql_output_injected_into_file/under_test.sql && echo OK

clean-test-output:
	rm -rf test_output
	mkdir -p test_output/example1
	mkdir -p test_output/sql_output_injected_into_file
