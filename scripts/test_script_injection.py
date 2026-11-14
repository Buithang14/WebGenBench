from playwright.sync_api import sync_playwright

test_script = """
<script>
window.testInjected = true;
console.log('Script in markdown executed!');
</script>
"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8501/", wait_until="networkidle")
    
    # Check if script in st.markdown runs
    # In Streamlit, markdown strips script tags for security.
    # But st.components.v1.html does not strip script tags!
    page.evaluate("""() => {
        // Let's test if st.components.v1.html can access window.parent
        console.log('Checking iframe access...');
    }""")
    browser.close()
