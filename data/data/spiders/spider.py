import scrapy
import os
import re
from scrapy.http import Response

class ArthritisSpider(scrapy.Spider):
    name = 'arthritis'
    start_urls = ['https://www.arthritisnsw.org.au/']
    
    def __init__(self):
        if not os.path.exists('content_files'):
            os.makedirs('content_files')
        self.visited_urls = set()
        
    def parse(self, response: Response):
        if response.url in self.visited_urls:
            self.log(f"Skipping already visited: {response.url}")
            return
        self.visited_urls.add(response.url)
        self.log(f"Visiting: {response.url}")
        
        # Generate from URL path
        url_path = response.url.replace('https://www.arthritisnsw.org.au', '').rstrip('/')
        filename = 'content_files/index.txt' if url_path == '' else f'content_files/{url_path.strip("/").replace("/", "_")}.txt'
        base_filename, counter = filename, 1
        while os.path.exists(filename):
            filename = f"{base_filename[:-4]}_{counter}.txt"
            counter += 1
        
        content = []
        title = response.css('title::text').get(default='No Title').strip()
        content.append(f"{title}\n{'=' * len(title)}")
        
        # Filtering contents
        main_content = response.css(
            'main, #content, .content, article, .entry-content, .main-content, '
            '.page-content, .post-content, div[class*="content"], div[id*="content"]'
        ) or response.css('body')  
        
        for heading in main_content.css('h1, h2, h3, h4, h5, h6'):
            heading_text = heading.css('::text').get(default='').strip()
            if heading_text:
                content.append(f"\n{heading_text}\n{'-' * len(heading_text)}")
                following_text = heading.xpath(
                    'following-sibling::*[not(self::script or self::style)]//text()'
                ).getall()
                paragraph_text = '\n'.join(t.strip() for t in following_text if t.strip() and not t.strip().startswith('@charset'))
                if paragraph_text:
                    content.append(paragraph_text)
        
        readable_elements = main_content.css(
            'p::text, li::text, blockquote::text, .entry-summary::text, .entry-content::text'
        ).getall()
        if readable_elements:
            cleaned_text = '\n'.join(t.strip() for t in readable_elements if t.strip() and not t.strip().startswith(('{', '.', '@')))
            if cleaned_text:
                content.append(f"\nAdditional Readable Content\n{'-' * 25}")
                content.append(cleaned_text)
        
        # Save content
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            self.log(f"Saved: {filename}")
        except Exception as e:
            self.log(f"Error saving {filename}: {str(e)}")
        
        # Follow all the links arthritisnsw.com
        href_links = response.css('a::attr(href)').getall()
        self.log(f"Found {len(href_links)} href links on {response.url}: {href_links[:10]}...")
        all_text = response.text
        potential_urls = re.findall(r'https?://www\.arthritisnsw\.org\.au[^\s\'"]*', all_text)
        self.log(f"Found {len(potential_urls)} potential URLs in raw HTML: {potential_urls[:10]}...")
        
        # Combine and follow links
        all_links = set(href_links + potential_urls)
        for url in all_links:
            if 'www.arthritisnsw.org.au' in url and url not in self.visited_urls:
                self.log(f"Queueing: {url}")
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    errback=self.handle_error
                )
            else:
                self.log(f"Skipping: {url}")
    
    def handle_error(self, failure):
        self.log(f"Request failed: {failure.request.url} - {str(failure)}")