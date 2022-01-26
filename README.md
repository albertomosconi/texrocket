# LaTeX Template Engine

A basic template engine for LaTeX. Create dynamic documents by parsing JSON data and populating a custom template.

The script parses a template and fills it with data read from json files. Provide different json files to have multiple files with the same structure but varying content. **Especially useful for translations**.

## Requirements
Make sure you have the following programs installed on your system before moving forward.
- [python](https://www.python.org/ "python.org")
- [virtualenv](https://virtualenv.pypa.io/en/latest/ "virtualenv.pypa.org") (optional, but recommended)

## Setup

Clone this repository in a folder of your choice and cd into it
```bash
git clone https://github.com/albertomosconi/latex-template-engine.git
cd latex-template-engine/
```
Create a virtual environment and activate it
```bash
virtualenv venv
source venv/bin/activate
```
Install the dependencies
```bash
pip install -r requirements.txt
```
You're all set!

## Usage
At any time you can run the script with the `-h` or `--help` flag to display usage information
```
usage: build.py [-h] [-i INPUT_JSON] [-o OUTPUT_DIR] [-v] input_tex

Dynamic LaTeX generation from JSON, developed by Alberto Mosconi

positional arguments:
  input_tex             the LaTeX template file

options:
  -h, --help            show this help message and exit
  -i INPUT_JSON, --input-json INPUT_JSON
                        the JSON file or directory of files
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        the directory for the output files
  -v, --verbose         print verbose output and save LaTeX logs
```

An example using all possible arguments is
```bash
python build.py example/TEMPLATE.tex -i example/ -o example/out/ -v
```
This will create an `out/` folder, with the documents generated using the `TEMPLATE.tex` template and the values inside `input.json` 
```
out/
├── source/
│   └── TEMPLATE_input.tex
├── TEMPLATE_input.log
└── TEMPLATE_input.pdf
```
**! All the JSON files MUST have the same structure**, the engine will create multiple documents (one for each `.json` file) starting from `TEMPLATE.tex`.

The generaed files have the following naming scheme
```
<TEMPLATE FILENAME>_<JSON FILENAME>.pdf
```
If the input JSON file is named `main.json` then this will not show up
```
<TEMPLATE FILENAME>.pdf
```

## Syntax

### Values

To display a certain JSON value reference it with the following syntax

```
<section.title>
```
```json
{
  "section": {
    "title": "The section title",
    "text": "some text"
  }
}
```
The example above will be rendered as `"The section title"`.

### Loops

You can avoid repetition of LaTeX code by using loops, which can be nested
```tex
\begin{itemize}
  %startloop: first
  \item <name>
    \begin{itemize}
      %startloop: second
      \item <name>
      %endloop
    \end{itemize}
  %endloop
\end{itemize}
```
```json
{
  "first": [
    {
      "name": "first main list item",
      "second": [
        { "name": "secondary list item" }
      ]
    },
    {
      "name": "second main list item",
      "second": [
        { "name": "secondary list item" }
      ]
    }
  ]
}
```
