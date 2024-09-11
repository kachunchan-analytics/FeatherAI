#!/usr/bin/env python
# coding: utf-8

import pyperclip
import os
from groq import Groq
import markdown
import requests
from bs4 import BeautifulSoup
import json

def loading_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

def get_clipboard_content():
    clipboard_content = pyperclip.paste()
    if "https://" in clipboard_content and " " not in clipboard_content:
        try:
            response = requests.get(clipboard_content)
            soup = BeautifulSoup(response.content, 'html.parser')
            clipboard_content = soup.find('body').text
        except requests.exceptions.RequestException as e:
            pass
    return clipboard_content

def generate_markdown_response(clipboard_content, config):
    groq_api_key = config['api_key']
    SYSTEM_PROMPT = config['system_prompt']
    user_command = config['user_prompt']

    client = Groq(api_key=groq_api_key)
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}"
        },
        {
            "role": "user",
            "content": f"{user_command}\n text_to_process:```{clipboard_content}```"
        }
    ],
    temperature=0.35,
    max_tokens=3000,
    top_p=0.9,
    stop=None,
    )
    response = completion.choices[0].message.content
    markdowned_responses = markdown.markdown(response, extensions=['tables'])
    return markdowned_responses

def generate_html_content(markdowned_responses):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FeatherAI Responses</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/turndown@7.1.1/dist/turndown.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1000px;
            margin: 40px auto;
            padding: 30px;
            background-color: #ffffff;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}
        .button-container {{
            margin-bottom: 20px;
            text-align: right;
        }}
        #copyButton, #arbitraryButton {{
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }}
        #copyButton:hover, #arbitraryButton:hover {{
            background-color: #2980b9; /* A slightly darker shade for better contrast */
        }}
        #copyButton.blackened, #arbitraryButton.blackened {{
            background-color: #000;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        h1 {{ font-size: 2.5em; border-bottom: 2px solid #e67e22; padding-bottom: 10px; }}
        h2 {{ font-size: 2em; }}
        h3 {{ font-size: 1.5em; }}
        p {{
            margin-bottom: 20px;
        }}
        ul, ol {{
            padding-left: 25px;
            margin-bottom: 20px;
        }}
        li {{
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 30px 0;
            font-size: 0.9em;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e8f4f8;
            transition: background-color 0.3s ease;
        }}
        code {{
            background-color: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 3px;
            padding: 2px 5px;
            font-family: 'Courier New', Courier, monospace;
        }}
        blockquote {{
            border-left: 4px solid #555;
            padding-left: 20px;
            margin-left: 0;
            font-style: italic;
            color: #555;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        a:hover {{
            color: #2980b9;
            text-decoration: underline;
        }}

        .textarea-container {{
            max-width: 1000px;
            margin: 40px auto;
            padding: 30px;
            background-color: #ffffff;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}
        textarea#arbitraryInput {{
            border: 2px solid #ccc; /* Yellow border */
            border-radius: 5px; /* Rounded corners */
            padding: 10px; /* Inner spacing */
            font-size: 16px; /* Font size */
            resize: none; /* Disable resizing */
            width: 97%; /* Full width */
            height: 20px; /* Limit height to 1 line */
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); /* Subtle shadow */
            transition: border-color 0.3s ease; /* Smooth border color transition */
        }}
        textarea#arbitraryInput:focus {{
            border-color: #007bff; /* Updated to blue on focus */
            outline: none; /* Remove default outline */
            border-width: 2px; /* Thicker border on focus */
        }}
    </style>
</head>
<body>
    <div style="background-color: #2c3e50; color: #ffffff; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">FeatherAI responses</div>
    <div class='textarea-container'>
        <textarea id="arbitraryInput" placeholder="Type your augmented user prompt here..."></textarea>
    </div>
    <div class='container'>
        <div class="button-container">
            <button id="arbitraryButton">Copy (Arbitrary)</button>
            <button id="copyButton">Copy Content</button>
        </div>
        <div id="markdownResponse">
            {markdowned_responses}
        </div>
    </div>

    <script>
        $(document).ready(function() {{
            const turndownService = new TurndownService({{
                codeBlockStyle: 'fenced',
                fence: '```',
                emDelimiter: '*',
                rules: []
            }});

            turndownService.addRule('tables', {{
                filter: ['table'],
                replacement: function(content, node) {{
                    const rows = node.rows;
                    const headerRow = rows[0];
                    const bodyRows = Array.from(rows).slice(1);
                    
                    let markdown = '\\n';

                    markdown += '| ' + Array.from(headerRow.cells).map(cell => cell.textContent.trim()).join(' | ') + ' |\\n';
                    markdown += '| ' + Array.from(headerRow.cells).map(() => '---').join(' | ') + ' |\\n';
                    bodyRows.forEach(row => {{
                        markdown += '| ' + Array.from(row.cells).map(cell => cell.textContent.trim()).join(' | ') + ' |\\n';
                    }});

                    return markdown + '\\n';
                }}
            }});

            turndownService.addRule('catchAll', {{
                filter: ['*'],
                replacement: function(content) {{
                    return content;
                }}
            }});

            function copyToClipboard(text, button) {{
                const tempElement = document.createElement('textarea');
                tempElement.value = text;
                document.body.appendChild(tempElement);
                tempElement.select();
                document.execCommand('copy');
                document.body.removeChild(tempElement);
                
                console.log("Content copied to clipboard");
                button.addClass("blackened");
            }}

            $('#copyButton').click(function() {{
                var response = document.getElementById('markdownResponse').innerHTML;
                var markdownResponse = turndownService.turndown(response);
                copyToClipboard(markdownResponse, $(this));
            }});
            $('#arbitraryButton').click(function() {{
                var response = document.getElementById('markdownResponse').innerHTML;
                var markdownResponse = turndownService.turndown(response);
                var userInput = document.getElementById('arbitraryInput').value; // Assuming the textarea has this ID
                var copyText =  userInput + "\\n\\n" + "```" + markdownResponse + "```";
                copyToClipboard(copyText, $(this));
            }});
        }});
    </script>
</body>
</html>
"""
def generate_html(html_content):
    with open("./historical_queries/featherai_responses.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
def open_html():
    cwd = os.getcwd()
    os.startfile(f"{cwd}/historical_queries/featherai_responses.html")

if __name__ == "__main__":
    config = loading_config()
    clipboard_content = get_clipboard_content()
    markdowned_responses = generate_markdown_response(clipboard_content, config)
    html_content = generate_html_content(markdowned_responses)
    generate_html(html_content)
    open_html()

