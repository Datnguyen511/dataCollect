go to data (the one with scrapy.cfg)

run the command: scrapy crawl arthritis

wait for it to crawl and proceed the data pulled from their website

put the folder content_files to process_data

run chunk_text.py. This will clean the data and create chunks if not created

run convert_chunks.py to get the json format for training (currently not the right format to use)

