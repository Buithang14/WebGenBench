from playwright.sync_api import sync_playwright

test_code = """
import streamlit as st
t1, t2 = st.tabs(["<b>Bold</b>", "Plain"])
with t1:
    st.write("tab 1")
"""

with open("dashboard/test_tab_html.py", "w", encoding="utf-8") as f:
    f.write(test_code)

print("Created test_tab_html.py")
