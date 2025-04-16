import inspect
import json

import httpx
import streamlit as st
from bs4 import BeautifulSoup

from simplify_html import extract_ssr_data, simplify_html_for_llm

st.set_page_config(page_title="HTML Simplifier for LLMs", page_icon="✨", layout="wide")

st.title("HTML Simplifier for LLMs")
st.markdown("""
This tool helps you prepare HTML content for Large Language Models (like ChatGPT) by:
1. Removing unnecessary elements
2. Preserving the structure and important content
3. Making it easier for LLMs to understand and write code to manipulate the HTML

**How to use:**
1. Paste your HTML or provide a URL
2. Get the simplified HTML
3. Copy the simplified HTML to use with your LLM
""")

# Input method selection at the top
input_method = st.radio("Choose input method:", ["Direct HTML", "URL"], horizontal=True)

html_content = ""

if input_method == "Direct HTML":
    html_content = st.text_area("Enter HTML content:", height=200, placeholder="Paste your HTML here...")
else:
    url = st.text_input("Enter URL:", placeholder="https://example.com")
    if url:
        try:
            with httpx.Client() as client:
                response = client.get(url)
                response.raise_for_status()
                html_content = response.text
                st.success("Successfully fetched HTML from URL!")
        except Exception as e:
            st.error(f"Error fetching URL: {str(e)}")

if html_content:
    with st.spinner("Simplifying HTML for LLM processing..."):
        try:
            # Prettify original HTML
            soup = BeautifulSoup(html_content, "html.parser")
            prettified_html = str(soup.prettify())  # Convert to string to fix type error

            simplified_html = simplify_html_for_llm(html_content)

            # Extract SSR data
            ssr_candidates = extract_ssr_data(html_content)

            # Add download buttons at the top of results
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Simplified HTML",
                    data=simplified_html,
                    file_name="simplified.html",
                    mime="text/html",
                )
            with col2:
                st.download_button(
                    label="Download Original HTML",
                    data=prettified_html,
                    file_name="original.html",
                    mime="text/html",
                )

            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["Original HTML", "Simplified HTML", "SSR Data"])

            with tab1:
                # Truncate large HTML content
                max_length = 10000  # Adjust this value as needed
                is_truncated = len(prettified_html) > max_length
                display_html = (prettified_html[:max_length] + "...") if is_truncated else prettified_html

                st.code(display_html, language="html", height=600, line_numbers=True)
                if is_truncated:
                    st.info("HTML content truncated. Use the download button above to get the full content.")

            with tab2:
                st.code(simplified_html, language="html", height=600, line_numbers=True)

            with tab3:
                if ssr_candidates:
                    st.success(f"Found {len(ssr_candidates)} SSR data candidates!")
                    for i, candidate in enumerate(ssr_candidates, 1):
                        st.subheader(f"SSR Candidate {i}")
                        if isinstance(candidate, dict):
                            st.json(candidate, expanded=False)
                        else:
                            st.code(json.dumps(candidate, indent=4), language="json")
                else:
                    st.info("No SSR data candidates found in the HTML.")

            # Show extract_ssr_data function code
            st.divider()
            st.subheader("Extract SSR Data Function")

            # Get the function code using inspect
            function_code = inspect.getsource(extract_ssr_data)

            # Define the required imports
            required_imports = """import base64
import html
import json
import re
from urllib.parse import unquote

from bs4 import BeautifulSoup"""

            # Display imports and function code
            st.code(required_imports + "\n\n" + function_code, language="python", line_numbers=True)

        except Exception as e:
            st.error(f"Error processing HTML: {str(e)}")
