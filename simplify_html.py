import argparse
import base64
import html
import json
import re
import sys
from urllib.parse import unquote

from bs4 import BeautifulSoup, Comment, NavigableString

from tailwind import Tailwind


def extract_ssr_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    ssr_candidates = []

    # 1. <script type="application/json">
    for script in soup.find_all("script", type="application/json"):
        if script.get("id", "").lower() in {"__ssr_data__", "ssr-data", "__next_data__"} or "ssr" in script.get("id", "").lower():
            try:
                ssr_candidates.append(json.loads(script.string))
            except Exception:
                pass

    # 2. Inline JS assignment: window.ssrData = {...};
    for script in soup.find_all("script", type=lambda x: x in [None, "text/javascript"]):
        script_text = script.string or ""
        # Match window.ssrData = { ... };
        match = re.search(r"window\.[\w_]+(?:\.[\w_]+)*\s*=\s*({[\s\S]*})\s*;?", script_text, re.DOTALL)
        if match:
            try:
                # Clean up the JSON string by removing extra whitespace and newlines
                json_str = re.sub(r'\s+', ' ', match.group(1)).strip()
                ssr_json = json.loads(json_str)
                ssr_candidates.append(ssr_json)
            except Exception:
                pass

        # 3. Match JSON.parse("{...}") style
        match = re.search(r'JSON\.parse\(\s*"(.*?)"\s*\)', script_text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1)
                json_str = json_str.encode().decode("unicode_escape")  # decode escaped characters
                ssr_json = json.loads(json_str)
                ssr_candidates.append(ssr_json)
            except Exception:
                pass

        # 4. Match base64-decoded SSR
        match = re.search(r'atob\("([^"]+)"(?:\.replace\(/&#x3D;/g,"="\))?\)', script_text)
        if match:
            try:
                base64_data = match.group(1).replace("&#x3D;", "=")  # handle HTML entity
                decoded = base64.b64decode(base64_data)
                # If escape(...) and decodeURIComponent(...) are used
                decoded = html.unescape(decoded.decode("utf-8"))  # handles escape()
                decoded = unquote(decoded)  # handles decodeURIComponent()
                ssr_json = json.loads(decoded)
                ssr_candidates.append(ssr_json)
                print(4)
            except Exception:
                pass

    # 5. <div id="..." data-ssr='...'>
    for tag in soup.find_all(True, attrs={"data-ssr": True}):
        try:
            data = json.loads(tag.attrs["data-ssr"])
            ssr_candidates.append(data)
        except Exception:
            pass

    return ssr_candidates


def is_tailwind_class(class_name: str) -> bool:
    """
    Check if a class name is likely a Tailwind CSS class using the Tailwind parser.

    Args:
        class_name (str): The class name to check

    Returns:
        bool: True if the class appears to be a Tailwind class
    """
    # Common semantic class names that should be preserved even though they might match patterns
    common_semantic_classes = [
        "container",
        "wrapper",
        "section",
        "content",
        "header",
        "footer",
        "sidebar",
        "nav",
        "main",
        "row",
        "column",
        "box",
        "card",
        "btn",
        "button",
        "input",
        "form",
        "modal",
        "dropdown",
        "menu",
        "list",
        "item",
        "page",
        "panel",
        "content-section",
        "custom-class",
        "my-wrapper",
    ]

    # Preserve these common semantic class names
    if class_name in common_semantic_classes:
        return False

    # Also preserve classes with semantic prefixes/suffixes
    if (
        class_name.endswith("-section")
        or class_name.endswith("-container")
        or class_name.endswith("-wrapper")
        or class_name.startswith("custom-")
        or class_name.startswith("js-")
        or class_name.startswith("my-")
    ):
        return False

    # Initialize Tailwind parser
    tw = Tailwind()

    # Split the class name into parts
    parts = class_name.split("-")

    # Check if the first part is a known Tailwind prefix
    if parts[0] in tw.classes:
        return True

    # Check for padding and margin utilities with decimal values
    if len(parts) >= 2:
        # Check for patterns like p-4, m-2, py-0.5, mx-1.5
        if parts[0] in ["p", "m", "px", "py", "pt", "pr", "pb", "pl", "mx", "my", "mt", "mr", "mb", "ml"]:
            # Try to convert the value to float to handle both integers and decimals
            try:
                float(parts[-1])
                return True
            except ValueError:
                # Check if it's a bracketed value like [20px]
                if parts[-1].startswith("[") and parts[-1].endswith("]"):
                    return True

    # Check for sizing utilities (w-4, h-10, etc.)
    if len(parts) == 2 and parts[0] in ["w", "h", "gap"] and parts[1].isdigit():
        return True

    # Check for color utilities like bg-gray-100, text-red-500, etc.
    if len(parts) >= 3 and parts[0] in ["bg", "text", "border"] and parts[1] in tw.colors:
        return True

    # Check for other common Tailwind patterns
    common_patterns = [
        r"^flex(-\w+)?$",
        r"^grid(-\w+)?$",
        r"^justify-\w+$",
        r"^items-\w+$",
        r"^space-[xy]-\d+$",
        r"^text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)$",
        r"^font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black)$",
        r"^rounded(-\w+)?$",
        r"^shadow(-\w+)?$",
        r"^opacity-\d+$",
        r"^z-\d+$",
        r"^order-\d+$",
        r"^col-span-\d+$",
        r"^row-span-\d+$",
        r"^translate-[xy]-\d+$",
        r"^scale-\d+$",
        r"^rotate-\d+$",
        r"^skew-[xy]-\d+$",
        r"^duration-\d+$",
        r"^delay-\d+$",
        r"^ease-\w+$",
        r"^blur(-\w+)?$",
        r"^brightness-\d+$",
        r"^contrast-\d+$",
        r"^grayscale(-\d+)?$",
        r"^hue-rotate-\d+$",
        r"^invert(-\d+)?$",
        r"^saturate-\d+$",
        r"^sepia(-\d+)?$",
        # Add patterns for pointer events and positioning
        r"^pointer-events-\w+$",
        r"^absolute$",
        r"^relative$",
        r"^fixed$",
        r"^sticky$",
        r"^static$",
        # Add patterns for group hover states
        r"^group-hover:[a-zA-Z0-9-]+$",
        # Add patterns for positioning utilities
        r"^-(top|right|bottom|left)-\d+$",
        # Add patterns for hover-related classes
        r"^hover[A-Z][a-zA-Z0-9]+$",
        # Add patterns for width and height utilities
        r"^w-(\d+|full|auto|screen)$",
        r"^h-(\d+|full|auto|screen)$",
        # Add patterns for responsive variants
        r"^(sm|md|lg|xl|2xl):[\w-]+(\[\d+px\])?$",
        # Add patterns for flex utilities
        r"^flex-(none|auto|initial|1|grow|shrink)$",
        # Add patterns for gap utilities
        r"^gap-\d+$",
        # Add pattern for hidden utility
        r"^hidden$",
        # Add pattern for group utility
        r"^group$",
    ]

    for pattern in common_patterns:
        if re.match(pattern, class_name):
            return True

    return False


def remove_tailwind_classes(soup: BeautifulSoup) -> None:
    """
    Remove Tailwind CSS classes from all elements while preserving other classes.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object to process
    """
    for element in soup.find_all(True):  # Find all elements
        if "class" in element.attrs:  # Check if element has class attribute
            # Get the class attribute value
            class_attr = element.attrs["class"]

            # Handle both string and list class attributes
            if isinstance(class_attr, str):
                classes = class_attr.split()
            else:
                classes = class_attr

            # Filter out Tailwind classes
            non_tailwind_classes = [cls for cls in classes if not is_tailwind_class(cls)]

            if non_tailwind_classes:
                element.attrs["class"] = non_tailwind_classes
            else:
                # If all classes were Tailwind classes, remove the class attribute entirely
                del element.attrs["class"]


def simplify_html_for_llm(html: str) -> str:
    """
    Simplifies HTML content by removing unnecessary elements for LLM processing.

    Args:
        html (str): The HTML content to simplify

    Returns:
        str: Simplified HTML with unnecessary elements removed
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for element in soup.find_all(["script", "style"]):
        element.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove meta tags
    for meta in soup.find_all("meta"):
        meta.decompose()

    # Remove link tags (except for hyperlinks)
    for link in soup.find_all("link"):
        link.decompose()

    # Remove noscript tags
    for noscript in soup.find_all("noscript"):
        noscript.decompose()

    # Remove empty elements
    for element in soup.find_all():
        if len(element.get_text(strip=True)) == 0 and not element.find_all():
            element.decompose()

    # Remove Tailwind classes
    remove_tailwind_classes(soup)

    # Fold lists or similar divs with more than 3 items
    for element in soup.find_all(["ul", "ol", "div"]):
        # Skip if element doesn't have direct children
        if not element.find_all(recursive=False):
            continue

        # Get all nodes (elements and text nodes)
        nodes = []
        for node in element.children:
            if isinstance(node, NavigableString):
                if node.strip():
                    nodes.append(node)
            else:
                nodes.append(node)

        # Detect list-like elements by checking patterns
        # 1. Check if there are multiple <li> tags (for ul, ol)
        # 2. Check if there are multiple <a> tags (common for linked lists)
        # 3. Check if there are multiple similar tags
        list_candidates = {}
        for node in nodes:
            if not hasattr(node, "name") or not node.name:
                continue
            if node.name not in list_candidates:
                list_candidates[node.name] = 0
            list_candidates[node.name] += 1

        # Find the most frequent tag that appears more than once
        list_tag = None
        max_count = 2  # At least 3 elements to be considered a list
        for tag, count in list_candidates.items():
            if count > max_count:
                max_count = count
                list_tag = tag

        # Find elements that are considered part of the list
        list_elements = [node for node in nodes if hasattr(node, "name") and node.name == list_tag] if list_tag else []

        if len(list_elements) > 3:
            # Keep track of what we've seen
            seen_elements = 0
            last_kept_element = None

            # Process all nodes
            for node in list(element.children):
                if hasattr(node, "name") and node.name == list_tag:
                    seen_elements += 1
                    if seen_elements > 3:
                        node.decompose()
                    else:
                        last_kept_element = node
                elif isinstance(node, NavigableString):
                    text = node.strip()
                    if text and "," in text:
                        if seen_elements > 3:
                            node.extract()
                        elif seen_elements == 3:
                            # Keep the comma after the third element and add ellipsis
                            node.replace_with(NavigableString(", ..."))
                        else:
                            # Keep the comma for elements 1 and 2
                            node.replace_with(NavigableString(", "))

            # If we haven't added ellipsis yet (no comma after third element)
            if last_kept_element is not None and not any("..." in str(n) for n in last_kept_element.next_siblings):
                last_kept_element.insert_after(" ...")

    return soup.prettify()


def main():
    parser = argparse.ArgumentParser(
        description="Simplify HTML content by removing unnecessary elements and folding long lists."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input HTML file (default: read from stdin)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file (default: write to stdout)",
    )

    args = parser.parse_args()

    try:
        html_content = args.input.read()
        simplified = simplify_html_for_llm(html_content)
        args.output.write(simplified)
    finally:
        if args.input != sys.stdin:
            args.input.close()
        if args.output != sys.stdout:
            args.output.close()


if __name__ == "__main__":
    main()
