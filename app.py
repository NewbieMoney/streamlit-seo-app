{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import requests\
from bs4 import BeautifulSoup\
import openai\
import re\
\
openai.api_key = st.secrets["OPENAI_API_KEY"]\
\
def scrape_top_results(query, num_results=3):\
    headers = \{"User-Agent": "Mozilla/5.0"\}\
    query = query.replace(' ', '+')\
    url = f"https://www.google.com/search?q=\{query\}"\
    response = requests.get(url, headers=headers)\
    soup = BeautifulSoup(response.text, 'html.parser')\
    links = []\
    for g in soup.find_all('a', href=True):\
        href = g['href']\
        if '/url?q=' in href:\
            clean_link = re.findall(r'/url\\\\?q=(.*?)&', href)\
            if clean_link:\
                links.append(clean_link[0])\
        if len(links) >= num_results:\
            break\
    return links\
\
def extract_text_from_url(url):\
    headers = \{"User-Agent": "Mozilla/5.0"\}\
    try:\
        r = requests.get(url, headers=headers, timeout=10)\
        soup = BeautifulSoup(r.text, 'html.parser')\
        paragraphs = soup.find_all('p')\
        return ' '.join([p.get_text() for p in paragraphs])\
    except:\
        return ""\
\
def generate_ai_content(keyword, competitor_texts):\
    prompt = f"""\
    Write a detailed SEO blog post for the keyword: \{keyword\}.\
    Use the following competitor content as reference:\
    \{competitor_texts\}\
    Make it original, locally relevant for Buffalo, New York, and include FAQs.\
    Include HTML formatting and headings (h1, h2, etc).\
    """\
    response = openai.ChatCompletion.create(\
        model="gpt-4",\
        messages=[\{"role": "user", "content": prompt\}],\
        temperature=0.7\
    )\
    return response.choices[0].message.content\
\
st.title("\uc0\u55357 \u56960  AI SEO Blog Generator for Lawyers")\
\
keyword = st.text_input("Enter your target keyword:", "Buffalo trucking attorney")\
\
if st.button("Generate Blog Post"):\
    with st.spinner("Scraping top results and generating content..."):\
        urls = scrape_top_results(keyword)\
        competitor_text = ""\
        for url in urls:\
            competitor_text += extract_text_from_url(url)[:3000]\
        ai_blog = generate_ai_content(keyword, competitor_text)\
\
        st.subheader("\uc0\u55357 \u56541  AI-Generated Blog Post")\
        st.code(ai_blog, language='html')\
\
        st.markdown("---")\
        st.write("Top Competitor URLs:")\
        for url in urls:\
            st.write(f"- \{url\}")\
}