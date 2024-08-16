# XSS Payload Converter

XSS Payload Converter is a versatile tool designed to help security professionals and ethical hackers generate, encode, and manipulate Cross-Site Scripting (XSS) payloads. The tool supports various encoding techniques and allows you to generate multiple payload combinations with ease, making it an essential utility for web application security testing.

## Features

- **Encoding Techniques**: Supports Unicode, Octal, Hexadecimal, HTML entity encoding, and Base64 encoding for payloads.
- **Combination Generator**: Generates payload combinations with options to specify the number of characters to encode and the types of encoding to apply.
- **Custom Character Encoding**: Allows you to specify exact characters to encode, giving you more control over the generated payloads.
- **Multi-threaded Processing**: Utilizes concurrent processing for faster payload generation.
- **PDF Output**: Save generated payloads directly as a PDF for easy sharing and documentation.
- **Command-Line Interface**: Simple and user-friendly CLI with detailed logging and verbose output options.

## Usage

```bash
python3 xss4ever.py -i input.txt -t unicode hex --count 10 --specify "XSS" --pdf output.pdf
```

- `-i, --input`: Input file with payloads (one per line).
- `-p, --payload`: Single payload input.
- `-o, --output`: Output file to save converted payloads.
- `-t, --types`: Conversion types to apply (`unicode`, `octal`, `hex`, `html`, `combine`, `base64`).
- `-c, --count`: Number of payloads to generate.
- `--random`: Number of characters to randomly encode.
- `--specify`: Specify characters to encode.
- `--verbose`: Enable verbose mode for detailed output.
- `--pdf`: Save output as a PDF file.

## Installation

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.x
- `colorama`
- `fpdf`
- `argparse`

## Commands

Basic Unicode Encoding of a Single Payload

bash

python3 xss4ever.py -p "<script>alert('XSS');</script>" -t unicode

Multiple Encoding Types with Input File

bash

python3 xss4ever.py -i payloads.txt -t unicode hex html -o encoded_payloads.txt

Generate Payloads with Random Character Encoding

bash

python3 xss4ever.py -p "<img src='x' onerror='alert(1)'>" -t hex octal --random 3

Combine Encoding Techniques with a Character Limit

bash

python3 xss4ever.py -p "<svg onload=alert(1)>" -t combine --random 5 -c 20

Specify Characters to Encode in Payload

bash

python3 xss4ever.py -p "<a href='javascript:alert(1)'>XSS</a>" -t html --specify "XSS"

Generate Payloads and Save Output as PDF

bash

python3 xss4ever.py -i payloads.txt -t base64 hex --count 10 --pdf output.pdf

Verbose Mode with Output Saved to a File

bash

python3 xss4ever.py -p "<iframe src='javascript:alert(1)'>" -t unicode -o result.txt --verbose

Custom Character Encoding with Limited Combinations

bash

python3 xss4ever.py -p "<img src=x onerror=alert('XSS')>" -t combine html --specify "XSS" --count 5

Base64 Encoding with PDF Output

bash

python3 xss4ever.py -p "<body onload=alert('XSS')>" -t base64 --pdf base64_payloads.pdf

Multi-Threaded Payload Generation from File

bash

python3 xss4ever.py -i input.txt -t unicode octal combine --count 50 --random 10 -o output.txt


## Contributing

Feel free to fork the repository, make changes, and submit a pull request. Any contributions to improve the tool or add new features are welcome.

