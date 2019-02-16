.PHONY: all test clean-test-output
.SILENT: clean-test-output

all: test

test: clean-test-output
	./facture.py --doctest
	./facture.py --conf-dir="tests/examples/example1" --output-type=json > test_output/example1/output.json
	diff tests/examples/example1/expected_output.json test_output/example1/output.json && echo OK

clean-test-output:
	rm -rf test_output
	mkdir -p test_output/example1
