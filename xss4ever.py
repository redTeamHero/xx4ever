import argparse
import sys
import random
import base64
import logging
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor
from fpdf import FPDF  # Import FPDF for PDF creation

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define characters to leave unchanged
SPECIAL_CHARS = " \n\t()'\"<>"

# Conversion Functions
def to_unicode(char):
    return f'\\u{ord(char):04x}' if len(char) == 1 else char

def to_octal(char):
    return f'\\{ord(char):03o}' if len(char) == 1 else char

def to_hex(char):
    return f'\\x{ord(char):02x}' if len(char) == 1 else char

def to_html(char):
    return f'&#{ord(char)};' if len(char) == 1 else char

def to_base64(payload):
    encoded_bytes = base64.b64encode(payload.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

def apply_encoding(char, encodings):
    for encoding in encodings:
        char = encoding(char)
    return char

def limited_combine(payload, limit=5):
    conversions = [to_unicode, to_octal, to_hex, to_html]
    positions = [i for i, char in enumerate(payload) if char.isalnum() and char not in SPECIAL_CHARS]
    selected_positions = random.sample(positions, min(len(positions), limit))
    result = list(payload)
    for pos in selected_positions:
        result[pos] = apply_encoding(payload[pos], [random.choice(conversions)])
    return ''.join(result)

def count_combinations(payloads, options, random_count=None):
    num_options = len(options)
    num_payloads = len(payloads)
    
    if 'combine' in options:
        max_length = max(len(payload) for payload in payloads)
        return num_payloads * (4 ** min(random_count or max_length, max_length))
    
    if random_count is not None:
        num_positions = max(len(payload) for payload in payloads)
        num_combinations = num_options ** min(random_count, num_positions)
        return num_payloads * num_combinations

    num_positions = max(len(payload) for payload in payloads)
    return num_payloads * (num_options ** num_positions)

def apply_random_encoding(payload, options, random_count):
    result = list(payload)
    positions = [i for i, char in enumerate(payload) if char.isalnum() and char not in SPECIAL_CHARS]
    
    if len(positions) == 0:
        return payload
    
    selected_positions = random.sample(positions, min(len(positions), random_count))
    
    conversions = {
        'unicode': to_unicode,
        'octal': to_octal,
        'hex': to_hex,
        'html': to_html
    }
    
    for pos in selected_positions:
        chosen_conversion = random.choice(options)
        if chosen_conversion in conversions:
            result[pos] = conversions[chosen_conversion](payload[pos])
    
    return ''.join(result)

def encode_text(text, types=None, specify_chars=None):
    conversions = {
        'unicode': to_unicode,
        'octal': to_octal,
        'hex': to_hex,
        'html': to_html
    }
    
    if types:
        active_conversions = [conversions[enc] for enc in types if enc in conversions]
    else:
        active_conversions = [to_unicode, to_octal, to_hex, to_html]
    
    if specify_chars:
        specify_chars = set(specify_chars)
        logging.debug(f"Specifying characters: {specify_chars}")
        encoded_text = ''.join(
            apply_encoding(char, active_conversions)
            if char in specify_chars and char not in SPECIAL_CHARS else char
            for char in text
        )
    else:
        encoded_text = ''.join(
            apply_encoding(char, active_conversions)
            if char.isalnum() and char not in SPECIAL_CHARS else char
            for char in text
        )
    
    logging.debug(f"Encoded text: {encoded_text}")
    return encoded_text

def generate_combinations(payloads, options, count, random_count=None, specify_chars=None):
    conversions = {
        'unicode': to_unicode,
        'octal': to_octal,
        'hex': to_hex,
        'html': to_html,
        'combine': limited_combine,
        'base64': to_base64
    }
    
    # Get all active conversions based on options
    active_conversions = [conversions[option] for option in options if option in conversions]
    logging.debug(f"Active conversions: {active_conversions}")
    
    all_combinations = []
    for payload in payloads:
        logging.debug(f"Processing payload: {payload}")
        
        if 'base64' in options:
            base64_payload = to_base64(payload)
            all_combinations.append(base64_payload)
            logging.debug(f"Base64 encoded payload: {base64_payload}")
            if len(all_combinations) >= count:
                break
        
        # If 'combine' is specified, use it separately
        if 'combine' in options:
            for _ in range(count):
                combined_payload = limited_combine(payload, random_count or 5)
                all_combinations.append(combined_payload)
                if len(all_combinations) >= count:
                    break
        else:
            # Apply all specified encodings in sequence
            if specify_chars:
                payload = encode_text(payload, types=options, specify_chars=specify_chars)
            else:
                payload = encode_text(payload, types=options)
                
            logging.debug(f"Encoded payload: {payload}")
            
            # Apply 'combine' encoding if specified
            if 'combine' in options:
                combined_payload = limited_combine(payload, random_count or 5)
                all_combinations.append(combined_payload)
            else:
                # Apply each encoding type in sequence
                for option in options:
                    if option in conversions and option not in ['combine', 'base64']:
                        converted_content = conversions[option](payload)
                        all_combinations.append(converted_content)
        
        if len(all_combinations) >= count:
            break
    
    logging.debug(f"Generated combinations: {all_combinations}")
    return all_combinations[:count]

def save_to_pdf(output, file_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for line in output:
        pdf.multi_cell(0, 10, line)
    
    pdf.output(file_path)

def process_args():
    parser = argparse.ArgumentParser(description="XSS Payload Converter")
    parser.add_argument("-i", "--input", help="Input file with payloads (one per line)")
    parser.add_argument("-p", "--payload", help="Single payload input")
    parser.add_argument("-o", "--output", help="Output file to save converted payloads")
    parser.add_argument("-t", "--types", nargs='+', choices=['unicode', 'octal', 'hex', 'html', 'combine', 'base64'], required=True, help="Conversion types to apply")
    parser.add_argument("-c", "--count", type=int, help="Number of payloads to generate")
    parser.add_argument("--random", type=int, help="Number of characters to randomly encode")
    parser.add_argument("--specify", type=str, help="Specify characters to encode")
    parser.add_argument("--verbose", action='store_true', help="Enable verbose mode for detailed output")
    parser.add_argument("--pdf", help="Save output as a PDF file")

    args = parser.parse_args()

    if not args.input and not args.payload:
        parser.error("Either --input or --payload must be specified.")
    
    if args.count and args.count <= 0:
        parser.error("--count must be a positive integer.")
    
    if args.random and args.random <= 0:
        parser.error("--random must be a positive integer.")
    
    return args

def main():
    args = process_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    payloads = []
    if args.input:
        try:
            with open(args.input, 'r') as file:
                payloads = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(Fore.RED + f"Error: The file {args.input} does not exist.")
            sys.exit(1)
    else:
        payloads.append(args.payload)
    
    total_combinations = count_combinations(payloads, args.types, args.random)
    print(Fore.YELLOW + f"Total possible payload combinations: {total_combinations}")

    if args.count:
        specify_chars = args.specify if args.specify else None
        with ThreadPoolExecutor() as executor:
            future = executor.submit(generate_combinations, payloads, args.types, args.count, args.random, specify_chars)
            generated_combinations = future.result()
        
        if generated_combinations:
            plain_output = '\n\n'.join(generated_combinations)  # Plain text output for file
            colored_output = '\n\n'.join([Fore.GREEN + comb + Style.RESET_ALL for comb in generated_combinations])  # Colored output for terminal
            
            if args.output:
                if args.pdf:
                    save_to_pdf(plain_output.splitlines(), args.output)
                    print(Fore.BLUE + f"Generated payloads saved as PDF to {args.output}")
                else:
                    with open(args.output, 'w') as file:
                        file.write(plain_output)
                    print(Fore.BLUE + f"Generated payloads saved to {args.output}")
            else:
                print(colored_output)
        else:
            print(Fore.RED + "No payloads generated.")

if __name__ == "__main__":
    main()
