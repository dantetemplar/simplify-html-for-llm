import httpx
import streamlit as st
from bs4 import BeautifulSoup

from simplify_html import simplify_html_for_llm

st.set_page_config(
    page_title="HTML Simplifier for LLMs",
    page_icon="✨",
    layout="wide"
)

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
input_method = st.radio(
    "Choose input method:",
    ["Direct HTML", "URL"],
    horizontal=True
)

html_content = ""

if input_method == "Direct HTML":
    html_content = st.text_area(
        "Enter HTML content:",
        height=200,
        placeholder="Paste your HTML here..."
    )
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
            prettified_html = soup.prettify()
            
            simplified_html = simplify_html_for_llm(html_content)
            
            # Add download button at the top of results
            st.download_button(
                label="Download Simplified HTML",
                data=simplified_html,
                file_name="simplified.html",
                mime="text/html"
            )
            
            # Display results in two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original HTML")
                # Truncate large HTML content
                max_length = 10000  # Adjust this value as needed
                is_truncated = len(prettified_html) > max_length
                display_html = (prettified_html[:max_length] + "...") if is_truncated else prettified_html
                
                st.code(display_html, language="html", height=600, line_numbers=True)
                if is_truncated:
                    st.download_button(
                        label="Download Full Original HTML",
                        data=prettified_html,
                        file_name="original.html",
                        mime="text/html",
                        key="download_original"
                    )
            
            with col2:
                st.subheader("Simplified HTML (Ready for LLM)")
                st.code(simplified_html, language="html", height=600, line_numbers=True)
        except Exception as e:
            st.error(f"Error processing HTML: {str(e)}") 