# Simple input output tester

This script can test your program with tests, provided in separate file.

## Usage

Write test file. Then execute:
```bash
python io-tester.py program_executable test_file
```

## Test file syntax

```
$test TESTNAME in
PROGRAM INPUT
$out
PROGRAM OUTPUT
$end

# Write as many as you need ...
```

## Comparison modes

You can provide comparison mode using `-c, --comp` option. These modes are supported:

1. EXACT - compares outputs character by character
2. NO_NEW_LINE - ignores new lines
3. NO_MULTIPLE_SPACES - treats multiple spaces as one
4. NO_ALL - ignores new lines and multiple spaces

## File mode

Use `-f, --filemode` flag to simulate program input from *input.txt* and take it's output from
*output.txt*. If flag is not passed tester uses *stdin* and *stdout*.
