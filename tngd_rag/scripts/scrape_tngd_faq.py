import json
import os
import re
from bs4 import BeautifulSoup

def build_knowledge_base():
    main_index_file = "tng_faq_page/main_faq.html" 
    articles_folder = "tng_faq_page/articles" 
    output_file = "../data/faq_data.json"
    base_url = "https://support.tngdigital.com.my"

    if not os.path.exists(main_index_file):
        print(f"Error: {main_index_file} not found!")
        return

    with open(main_index_file, "r", encoding="utf-8") as f:
        index_soup = BeautifulSoup(f.read(), "html.parser")

    final_data = []
    category_headers = index_soup.find_all(class_="section-tree-title")

    for header in category_headers:
        category_name = header.get_text(strip=True)
        parent_section = header.find_parent() 
        
        if parent_section:
            links = parent_section.find_all('a', href=True)
            for link in links:
                href = link['href']
                if "/hc/en-my/articles/" in href:
                    match = re.search(r'articles/(\d+)', href)
                    if not match: continue
                    article_id = match.group(1)
                    
                    target_file = None
                    if os.path.exists(articles_folder):
                        for filename in os.listdir(articles_folder):
                            if article_id in filename and filename.endswith(".html"):
                                target_file = os.path.join(articles_folder, filename)
                                break
                    
                    if target_file:
                        with open(target_file, "r", encoding="utf-8") as af:
                            article_soup = BeautifulSoup(af.read(), "html.parser")
                        
                        article_box = article_soup.find("article", class_="article")
                        
                        if article_box:
                            # 1. Target the specific sections
                            art_header = article_box.find("header", class_="article-header")
                            art_info = article_box.find("section", class_="article-info")
                            
                            # 2. REMOVE THE AUTHOR TAG COMPLETELY
                            if art_header:
                                author_tag = art_header.find("div", class_="article-author")
                                if author_tag:
                                    author_tag.decompose() # Destroys the tag and its children
                            
                            # 3. Extract cleaned text
                            header_text = art_header.get_text(" ", strip=True) if art_header else ""
                            info_text = art_info.get_text(" ", strip=True) if art_info else ""
                            
                            answer_text = f"{header_text} {info_text}".strip()
                            
                            h1_tag = art_header.find("h1") if art_header else None
                            question = h1_tag.get_text(strip=True) if h1_tag else link.get_text(strip=True)
                            
                            sentences = re.split(r'(?<=[.!?])\s+', answer_text)
                            summary = " ".join(sentences[:2]) if len(sentences) >= 2 else answer_text
                        else:
                            question = link.get_text(strip=True)
                            answer_text = "-"
                            summary = "-"
                    else:
                        question = link.get_text(strip=True)
                        answer_text = "-"
                        summary = "-"

                    final_data.append({
                        "question": question,
                        "summary": summary,
                        "answer": answer_text if answer_text else "-",
                        "url": href.split('?')[0],
                        "category": category_name
                    })

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    print(f"Extraction complete! Saved to {output_file}")

if __name__ == "__main__":
    build_knowledge_base()