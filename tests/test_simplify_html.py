from simplify_html import simplify_html_for_llm


def test_removes_script_tags():
    html = """
    <html>
        <head>
            <script>alert('test');</script>
        </head>
        <body>
            <p>Hello World</p>
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    assert '<script>' not in simplified
    assert 'alert' not in simplified
    assert 'Hello World' in simplified

def test_removes_style_tags():
    html = """
    <html>
        <head>
            <style>
                body { color: red; }
            </style>
        </head>
        <body>
            <p>Hello World</p>
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    assert '<style>' not in simplified
    assert 'color: red' not in simplified
    assert 'Hello World' in simplified

def test_removes_comments():
    html = """
    <html>
        <body>
            <!-- This is a comment -->
            <p>Hello World</p>
            <!-- Another comment -->
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    assert '<!--' not in simplified
    assert 'Hello World' in simplified

def test_removes_meta_tags():
    html = """
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width">
        </head>
        <body>
            <p>Hello World</p>
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    assert '<meta' not in simplified
    assert 'Hello World' in simplified

def test_removes_link_tags():
    html = """
    <html>
        <head>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <p>Hello World</p>
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    assert '<link' not in simplified
    assert 'Hello World' in simplified

def test_removes_noscript_tags():
    html = """
    <html>
        <body>
            <noscript>
                Please enable JavaScript
            </noscript>
            <p>Hello World</p>
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    assert '<noscript>' not in simplified
    assert 'Please enable JavaScript' not in simplified
    assert 'Hello World' in simplified

def test_removes_empty_elements():
    html = """
    <html>
        <body>
            <div></div>
            <p>Hello World</p>
            <span></span>
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    assert '<div></div>' not in simplified
    assert '<span></span>' not in simplified
    assert 'Hello World' in simplified

def test_preserves_important_content():
    html = """
    <html>
        <body>
            <h1>Title</h1>
            <p>This is a paragraph with <strong>important</strong> content.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <a href="https://example.com">Link</a>
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    assert 'Title' in simplified
    assert 'important' in simplified
    assert 'Item 1' in simplified
    assert 'Item 2' in simplified
    assert 'Link' in simplified

def test_folds_lists_with_more_than_3_items():
    html = """
    <html>
        <body>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
                <li>Item 4</li>
                <li>Item 5</li>
            </ul>
            <ol>
                <li>First</li>
                <li>Second</li>
                <li>Third</li>
                <li>Fourth</li>
            </ol>
            <div>
                <div>Div 1</div>
                <div>Div 2</div>
                <div>Div 3</div>
                <div>Div 4</div>
                <div>Div 5</div>
                <div>Div 6</div>
            </div>
        </body>
    </html>
    """
    simplified = simplify_html_for_llm(html)
    
    # Check that lists are folded to 3 items plus "..."
    assert 'Item 1' in simplified
    assert 'Item 2' in simplified
    assert 'Item 3' in simplified
    assert 'Item 4' not in simplified
    assert 'Item 5' not in simplified
    assert '...' in simplified
    
    # Check ordered list
    assert 'First' in simplified
    assert 'Second' in simplified
    assert 'Third' in simplified
    assert 'Fourth' not in simplified
    
    # Check div folding
    assert 'Div 1' in simplified
    assert 'Div 2' in simplified
    assert 'Div 3' in simplified
    assert 'Div 4' not in simplified
    assert 'Div 5' not in simplified
    assert 'Div 6' not in simplified

def test_folds_comma_separated_lists():
    html = """
    <div class="tagContainer">
        <span>Related Objects:</span>
        <a href="/search?q=class:paper">paper</a>,
        <a href="/search?q=class:rock">rock</a>,
        <a href="/search?q=class:scissors">scissors</a>,
        <a href="/search?q=class:scissor">scissor</a>,
        <a href="/search?q=class:papel">papel</a>
    </div>
    """
    simplified = simplify_html_for_llm(html)

    # Check that only first 3 items are kept
    assert 'paper' in simplified
    assert 'rock' in simplified
    assert 'scissors' in simplified
    assert 'href="/search?q=class:scissor"' not in simplified
    assert 'href="/search?q=class:papel"' not in simplified
    assert '...' in simplified

def test_handles_mixed_content():
    html = """
    <div>
        <p>Some text</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
            <li>Item 4</li>
        </ul>
        <div class="tags">
            <a>tag1</a>,
            <a>tag2</a>,
            <a>tag3</a>,
            <a>tag4</a>,
            <a>tag5</a>
        </div>
    </div>
    """
    simplified = simplify_html_for_llm(html)

    # Check list folding
    assert 'Item 1' in simplified
    assert 'Item 2' in simplified
    assert 'Item 3' in simplified
    assert 'Item 4' not in simplified
    assert '...' in simplified

    # Check tag folding
    assert 'tag1' in simplified
    assert 'tag2' in simplified
    assert 'tag3' in simplified
    assert 'tag4' not in simplified
    assert 'tag5' not in simplified
    # Check for comma and ellipsis after tag3
    assert any(line.strip() == 'tag3' for line in simplified.splitlines())
    assert any('...' in line for line in simplified.splitlines())

def test_preserves_formatting():
    html = """
    <div class="container">
        <div class="header">
            <h1>Title</h1>
        </div>
        <div class="content">
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
            <p>Paragraph 3</p>
            <p>Paragraph 4</p>
            <p>Paragraph 5</p>
        </div>
    </div>
    """
    simplified = simplify_html_for_llm(html)
    
    # Check that content is folded properly
    assert 'Paragraph 1' in simplified
    assert 'Paragraph 2' in simplified
    assert 'Paragraph 3' in simplified
    assert 'Paragraph 4' not in simplified
    assert 'Paragraph 5' not in simplified
    assert 'Paragraph 3' in simplified
    assert '...' in simplified

def test_cli_functionality(tmp_path):
    # Create a test HTML file
    test_html = """
    <html>
        <body>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
                <li>Item 4</li>
            </ul>
        </body>
    </html>
    """
    input_file = tmp_path / "input.html"
    output_file = tmp_path / "output.html"
    
    # Write test HTML to input file
    input_file.write_text(test_html)
    
    # Import the main function
    # Mock sys.argv
    import sys

    from simplify_html import main
    original_argv = sys.argv
    sys.argv = ["simplify_html.py", str(input_file), "-o", str(output_file)]
    
    try:
        # Run the CLI
        main()
        
        # Read the output
        output = output_file.read_text()
        
        # Verify the output
        assert 'Item 1' in output
        assert 'Item 2' in output
        assert 'Item 3' in output
        assert 'Item 4' not in output
        assert '...' in output
    finally:
        # Restore original argv
        sys.argv = original_argv

def test_removes_tailwind_classes():
    html = """
    <div class="my-wrapper">
        <div class="flex justify-between items-center p-4 bg-gray-100">
            <h1 class="text-2xl font-bold text-gray-900">Title</h1>
            <div class="custom-class flex items-center gap-2">
                <span class="text-sm text-gray-500">Subtitle</span>
            </div>
        </div>
        <div class="content-section">
            <p class="leading-6 text-gray-700">Content</p>
        </div>
    </div>
    """
    simplified = simplify_html_for_llm(html)
    
    # Check that Tailwind classes are removed
    assert 'flex' not in simplified
    assert 'justify-between' not in simplified
    assert 'items-center' not in simplified
    assert 'p-4' not in simplified
    assert 'bg-gray-100' not in simplified
    assert 'text-2xl' not in simplified
    assert 'font-bold' not in simplified
    assert 'text-gray-900' not in simplified
    assert 'gap-2' not in simplified
    assert 'text-sm' not in simplified
    assert 'text-gray-500' not in simplified
    assert 'leading-6' not in simplified
    assert 'text-gray-700' not in simplified
    
    # Check that non-Tailwind classes are preserved
    assert 'class="my-wrapper"' in simplified
    assert 'class="custom-class"' in simplified
    assert 'class="content-section"' in simplified
    
    # Check that content is preserved
    assert 'Title' in simplified
    assert 'Subtitle' in simplified
    assert 'Content' in simplified

def test_removes_tailwind_classes_completely():
    html = """
    <div>
        <div class="flex justify-between p-4">
            <h1 class="text-2xl font-bold">Title</h1>
            <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">Subtitle</span>
            </div>
        </div>
        <div class="mt-4 p-4">
            <p class="leading-6 text-gray-700">Content</p>
        </div>
    </div>
    """
    simplified = simplify_html_for_llm(html)
    
    # Check that elements with only Tailwind classes have their class attributes completely removed
    assert 'class=' not in simplified
    
    # Verify content is preserved
    assert 'Title' in simplified
    assert 'Subtitle' in simplified
    assert 'Content' in simplified

def test_handles_hover_tooltip():
    html = """
    <div class="group">
        <div class="hoverTooltip pointer-events-none absolute -right-4 -top-2 group-hover:opacity-100">
            <span>Go to Universe Home</span>
        </div>
    </div>
    """
    simplified = simplify_html_for_llm(html)
    
    # Check that the tooltip content is preserved
    assert 'Go to Universe Home' in simplified
    # Check that Tailwind classes are removed
    assert 'pointer-events-none' not in simplified
    assert 'absolute' not in simplified
    assert 'group-hover:opacity-100' not in simplified
    # Check that the structure is simplified
    assert 'hoverTooltip' not in simplified

def test_handles_navbar_structure():
    html = """
    <div class="navbarContainer2 h-16 w-full md:h-full md:w-[56px]" data-ssr="true" id="SSRGlobalNavbar">
        <nav class="dark collapsed navbar2 flex h-16 flex-col md:h-full md:px-2 md:py-6">
            <div class="hidden h-full w-full flex-col justify-between gap-2 md:flex">
                <div class="flex flex-col gap-3 pt-2">
                    <div class="logo-container group relative flex w-full flex-none items-center justify-center py-0.5">
                        <span>Navigation Content</span>
                    </div>
                </div>
            </div>
        </nav>
    </div>
    """
    simplified = simplify_html_for_llm(html)
    
    # Check that important structural classes and attributes are preserved
    assert 'navbarContainer2' in simplified
    assert 'navbar2' in simplified
    assert 'logo-container' in simplified
    assert 'data-ssr="true"' in simplified
    assert 'id="SSRGlobalNavbar"' in simplified
    
    # Check that content is preserved
    assert 'Navigation Content' in simplified
    
    # Check that Tailwind classes are removed
    assert 'h-16' not in simplified
    assert 'w-full' not in simplified
    assert 'md:h-full' not in simplified
    assert 'md:w-[56px]' not in simplified
    assert 'flex-col' not in simplified
    assert 'justify-between' not in simplified
    assert 'items-center' not in simplified
    assert 'py-0.5' not in simplified
