#!/usr/bin/env python3
import re, json, os, shutil, sys, argparse
from copy import copy, deepcopy
from pdflatex import PDFLaTeX

def exit_with_error(message):
    print(f"\033[91mERROR: {message}\033[00m")
    sys.exit(1)

def setup_arg_parser():
    parser = argparse.ArgumentParser(description="Dynamic LaTeX generation from JSON")
    parser.add_argument("input_tex", help="the LaTeX template file")
    parser.add_argument("-i", "--input-json", help="the JSON file")
    parser.add_argument("-o", "--output-dir", help="the directory for the output files", default=".")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
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

def main():
    args, print_usage = setup_arg_parser()
    validate_args(args, print_usage)

if __name__ == "__main__":
    main()

sys.exit(0)

pdfname = "latex-template-engine"

languages = []
inputs = {}
outputs = {}

with open("TEMPLATE.tex", 'r') as template:
    content = template.readlines()

files = os.listdir("./content")
for file in list(filter(lambda f: f.endswith(".json"), files)):
    l = file[:-5]
    languages.append(l)
    outputs[l] = []

for lang in languages:
    with open(f"content/{lang}.json", 'r') as lin:
        inputs[lang] = json.load(lin)

try:
    shutil.rmtree("./out")
except FileNotFoundError as e:
    pass
os.makedirs("./out/sources")


def handle_loop(start_index, object_base, reset_stack):
    # print("loop loop")
    start_index = copy(start_index)
    y = start_index
    line = content[y]
    ireset = copy(y)
    reset_stack.insert(0, copy(y))
    for loopit in object_base:
        y = ireset
        line = content[y]
        while re.search("%endloop", line) == None:
            # print(y+1, line[:-1])
            if re.search("%startloop:", line) != None:
                jsonpath = line.split("%startloop: ")[1][:-1].split(".")
                # print(jsonpath)
                loopcontent = deepcopy(loopit)
                for key in jsonpath:
                    loopcontent = loopcontent[key]
                y = handle_loop(y+1, loopcontent, reset_stack)
                line = content[y]
            else:
                contentmatches = re.findall("<[a-zA-Z]+\.?[a-zA-Z]+>",line)
                loopline = line
                for match in contentmatches:
                    jsonpath = match[1:-1].split(".")
                    text = loopit
                    for key in jsonpath:
                        text = text[key]
                    
                    loopline = loopline.replace(match, text)
                # print(loopline[:-1])
                outputs[lang].append(loopline)
                y+=1
                line = content[y]
    reset_stack.pop(0)
    # print("end loop")
    return y+1
    

for lang in languages:
    print(f"Building {lang}...", end='\r')
    i = 0
    while i < len(content):
        line = content[i]
        # print(i+1, line[:-1])
        if re.search("%startloop:", line) != None:
            jsonpath = line.split("%startloop: ")[1][:-1].split(".")
            # print(jsonpath)
            loopcontent = deepcopy(inputs[lang])
            for key in jsonpath:
                loopcontent = loopcontent[key]
            i = handle_loop(i+1, loopcontent, [])
            line = content[i]
            # print("finished loop")
        else:
            contentmatches = re.findall("<[a-zA-Z]+\.?[a-zA-Z]+>",line)
            for match in contentmatches:
                jsonpath = match[1:-1].split(".")
                text = inputs[lang]
                for key in jsonpath:
                    text = text[key]
                
                line = line.replace(match, text)

        outputs[lang].append(line)
        i+=1

    outfilename =f"{pdfname}.tex"
    if lang != "default":
        outfilename = outfilename[:-4] + f"_{lang}.tex"

    with open(f"./out/sources/{outfilename}", 'w') as out:
        out.writelines(outputs[lang])

    os.chdir("./out")
    
    pdfl = PDFLaTeX.from_texfile(f"./sources/{outfilename}")
    pdf, log, completed_process = pdfl.create_pdf(keep_pdf_file=True, keep_log_file=False)
    os.chdir("..")

    print(f"Building '{lang}'... done.")