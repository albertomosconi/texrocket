#!/usr/bin/env python3
import re, json, os, sys, argparse
from pdflatex import PDFLaTeX

def exit_with_error(message):
    print(f"\033[91mERROR: {message}\033[00m")
    sys.exit(1)

def setup_arg_parser():
    parser = argparse.ArgumentParser(description="Dynamic LaTeX generation from JSON, developed by Alberto Mosconi")
    parser.add_argument("input_tex", help="the LaTeX template file")
    parser.add_argument("-i", "--input-json", help="the JSON file or directory of files")
    parser.add_argument("-o", "--output-dir", help="the directory for the output files", default=".")
    parser.add_argument("-v", "--verbose", help="print verbose output and save LaTeX logs", action="store_true")
    return parser.parse_args(), parser.print_usage

def validate_args(args, print_usage):
    if not os.path.exists(args.input_tex):
        print_usage()
        exit_with_error("LaTeX template: File does not exist")

    elif not args.input_tex.endswith(".tex"):
        print_usage()
        exit_with_error("LaTeX template: Invalid format")

    if args.input_json:
        input_json = args.input_json

        if not os.path.exists(input_json):
            print_usage()
            exit_with_error("Input JSON: File does not exist")

        elif os.path.isfile(input_json) and not input_json.endswith(".json"):
            print_usage()
            exit_with_error("Input JSON: Invalid file type")
        
        elif os.path.isdir(input_json):
            dir_content = os.listdir(input_json)
            if len(list(filter(lambda f: f.endswith(".json"), dir_content))) < 1:
                print_usage()
                exit_with_error("Input JSON: No JSON files found in folder")

def get_list_of_json_input_files(raw_dir_or_file):
    json_inputs = []
    if raw_dir_or_file:
        if os.path.isdir(raw_dir_or_file):
            filtered = list(filter(lambda f: f.endswith(".json"), os.listdir(raw_dir_or_file)))
            json_inputs = [os.path.join(raw_dir_or_file, f) for f in filtered]
        else:
            json_inputs = [raw_dir_or_file]

    return json_inputs

def get_dict_value_from_path(d, keys):
    value = d
    for key in keys:
        value = value.get(key)
    return value

def parse_line(line, obj):
    parsed = line
    var_matches = re.findall("<[a-zA-Z]+\.?[a-zA-Z]+>", parsed)
    for match in var_matches:
        jsonpath = match[1:-1].split(".")
        parsed_value = get_dict_value_from_path(obj, jsonpath)        
        parsed = parsed.replace(match, parsed_value)
    return parsed

def handle_loop(start_index, object_list, all_lines, output_lines):
    current_index = start_index
    # TODO: check if list of objects is empty
    for obj in object_list:
        current_index = start_index
        current_line = all_lines[current_index]

        while re.search("%endloop", current_line) == None:
            parsed_line = ""
            if re.search("%startloop:", current_line) != None:
                jsonpath = current_line.split("%startloop: ")[1][:-1].split(".")
                sub_dict = get_dict_value_from_path(obj, jsonpath)
                current_index = handle_loop(current_index + 1, sub_dict, all_lines, output_lines)
                current_line = all_lines[current_index]
                parsed_line = current_line

            else:
                parsed_line = parse_line(current_line, obj)

            output_lines.append(parsed_line)
            current_index += 1
            current_line = all_lines[current_index]

    return current_index + 1

def save_and_compile_tex(out_dir, filename, lines, logs=False):
    # create output folder if it doesnt exist
    complete_out_dir = os.path.join(out_dir, "source")
    if not os.path.isdir(complete_out_dir):
        os.makedirs(complete_out_dir)

    open(f"{os.path.join(complete_out_dir, filename)}.tex", "w").writelines(lines)

    root_dir = os.getcwd()
    os.chdir(out_dir)
    # generate pdfs
    pdfl = PDFLaTeX.from_texfile(f"{os.path.join('source', filename)}.tex")
    pdfl.create_pdf(keep_pdf_file=True, keep_log_file=logs)
    os.chdir(root_dir)
    return

def main():
    args, print_usage = setup_arg_parser()
    validate_args(args, print_usage)
    verbose_print = print if args.verbose else lambda *a, **k: None

    input_files = get_list_of_json_input_files(args.input_json)
    template_file_lines = open(args.input_tex, 'r').readlines()

    if len(input_files) == 0:
        verbose_print("No JSON inputs were given, compiling LaTeX template directly...")
        output_filename = f"{args.input_tex[:-4]}"
        save_and_compile_tex(args.output_dir, output_filename, template_file_lines, logs=args.verbose)

    for json_file in input_files:
        json_filename_no_ext = os.path.split(json_file)[1][:-5]
        verbose_print(f"Processing '{json_filename_no_ext}.json'...")
        json_obj = json.load(open(json_file, 'r'))

        line_number = 0
        output_lines = []
        while line_number < len(template_file_lines):
            current_template_line = template_file_lines[line_number]
            # verbose_print(current_template_line[:-1])
            parsed_line = ""
            if re.search("%startloop:", current_template_line) != None:
                # verbose_print("Begin loop")
                jsonpath = current_template_line.split("%startloop: ")[1][:-1].split(".")
                sub_dict = get_dict_value_from_path(json_obj, jsonpath)
                line_number = handle_loop(line_number + 1, sub_dict, template_file_lines, output_lines)
                current_template_line = template_file_lines[line_number]
                parsed_line = current_template_line

            else:
                parsed_line = parse_line(current_template_line, json_obj)

            output_lines.append(parsed_line)
            line_number += 1

        # write the parsed source file
        output_filename = f"{args.input_tex[:-4]}"
        if json_filename_no_ext != "main":
            output_filename += f"_{json_filename_no_ext}"

        save_and_compile_tex(args.output_dir, output_filename, output_lines, logs=args.verbose)
        
    verbose_print("Done.")

if __name__ == "__main__":
    main()
