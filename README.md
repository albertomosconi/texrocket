# LaTeX Template Engine

A basic template engine for LaTeX. Create dynamic LaTeX documents by parsing JSON data and populating a custom template.

The script parses a template and fills it with data read from json files. Provide different json files to have multiple files with the same structure but varying content. **Especially useful for translations**.

## Requirements
Make sure you have the following programs installed on your system before moving forward.
- [python](https://www.python.org/ "python.org")
- [virtualenv](https://virtualenv.pypa.io/en/latest/ "virtualenv.pypa.org")

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

The `contents/` folder holds your JSON files that will be parsed, for example:
```json
{
  "section": {
    "title": "The section title",
    "text": "some text"
  }
}
```
**! All the JSON files MUST have the same structure**, the engine will create multiple documents (one for each `.json` file inside `contents/`) starting from `TEMPLATE.tex`.

### Values

To display a certain JSON value reference it with the following syntax

```
<section.title>
```
With the example above, this will be rendered as `"The section title"`.

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

### Execution

To run the script and generate the documents simply execute
```bash
python build.py
```
The outputs will be in the `out/` folder.
