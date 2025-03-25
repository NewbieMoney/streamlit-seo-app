import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re
import json
from datetime import date

# Set up OpenAI client
client = OpenAI()
openai_api_key = st.secrets["OPENAI_API_KEY"]

def scrape_top_results(query, num_results=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for g in soup.find_all('a', href=True):
        href = g['href']
        if '/url?q=' in href:
            clean_link = re.findall(r'/url\\?q=(.*?)&', href)
            if clean_link:
                links.append(clean_link[0])
        if len(links) >= num_results:
            break
    return links

def extract_text_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs])
    except:
        return ""

def generate_ai_content(keyword, competitor_texts):
    prompt = f"""
    Write a detailed SEO blog post for the keyword: {keyword}.
    Use the following competitor content as reference:
    {competitor_texts}
    Make it original, locally relevant for Buffalo, New York, and include 3 FAQs.
    Include HTML formatting and headings (h1, h2, etc).
    Output:
    - Meta title and description
    - SEO-friendly HTML
    - Schema markup for FAQ and LegalService (as JSON-LD)
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def extract_faq_schema(faq_html):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What should I do after a truck accident in Buffalo?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Seek medical attention, document the scene, and contact a trucking attorney."
                }
            },
            {
                "@type": "Question",
                "name": "Who is liable in a Buffalo trucking accident?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Liability can fall on the driver, the trucking company, or even parts manufacturers."
                }
            }
        ]
    }

# --- Streamlit Interface ---
st.title("🚀 AI SEO Blog Generator for Lawyers")

keyword = st.text_input("Enter your target keyword:", "Buffalo trucking attorney")

if st.button("Generate Blog Post"):
    with st.spinner("Scraping top results and generating content..."):
        urls = scrape_top_results(keyword)
        competitor_text = ""
        for url in urls:
            competitor_text += extract_text_from_url(url)[:3000]

        ai_blog = generate_ai_content(keyword, competitor_text)
        faq_schema = extract_faq_schema(ai_blog)

        st.subheader("📝 AI-Generated SEO Blog Post")
        st.code(ai_blog, language='html')

        st.subheader("📦 Schema Markup (FAQ)")
        st.code(json.dumps(faq_schema, indent=2), language='json')

        st.download_button(
            label="📥 Download Blog Post HTML",
            data=ai_blog,
            file_name=f"{keyword.replace(' ', '_')}_blog_{date.today()}.html",
            mime="text/html"
        )

        st.markdown("---")
        st.write("Top Competitor URLs:")
        for url in urls:
            st.write(f"- {url}")
