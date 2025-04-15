# HTML Simplifier for LLMs

A tool to simplify HTML content for better processing by Large Language Models (LLMs) like ChatGPT.

## 🚀 [Try the Demo](https://dantetemplar-simplifier.streamlit.app)

## Features

The tool cleans HTML by:
- Removing scripts, styles, and comments
- Removing meta tags and link tags
- Removing empty elements
- Removing Tailwind CSS classes
- Folding long lists (keeping only first 3 items)
- Preserving important structure and content

## Example

Here's an example of HTML before and after simplification:

### Original HTML
```html
<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
    <meta charset="utf-8">
    <link rel="stylesheet" href="styles.css">
    <script src="script.js"></script>
    <style>
        .custom-class { color: red; }
    </style>
</head>
<body>
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold">Welcome</h1>
        <ul class="list-disc">
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
            <li>Item 4</li>
            <li>Item 5</li>
        </ul>
        <!-- This is a comment -->
        <div class="empty-div"></div>
    </div>
</body>
</html>
```

### Simplified HTML
```html
<html>
<body>
    <div>
        <h1>Welcome</h1>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
            ...
        </ul>
    </div>
</body>
</html>
```

## Development

1. Install dependencies using `uv`:
    ```bash
    uv sync
    ```
2. Run the Streamlit app:
    ```bash
    uv run streamlit run app.py
    ```
3. Choose your input method:
   - **Direct HTML**: Paste your HTML content directly
   - **URL**: Enter a URL to fetch HTML from

4. The app will show both original and simplified HTML side by side

### Running Tests
```bash
uv run python -m pytest
```

### Adding Dependencies
```bash
uv add <package-name>
```
