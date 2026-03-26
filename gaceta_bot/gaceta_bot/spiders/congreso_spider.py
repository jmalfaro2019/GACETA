import scrapy
import re
import os
import json
from confluent_kafka import Producer


class CongresoSpider(scrapy.Spider):
    name = 'congreso'
    start_urls = ['https://svrpubindc.imprenta.gov.co/senado/']
    total_pages = 1
    total_documents = 1
    # Create a folder to save results
    os.makedirs("documents", exist_ok=True)
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3 
    }
    
    def __init__(self, *args, **kwargs):
        super(CongresoSpider, self).__init__(*args, **kwargs)
        # 2. Connect to your local Kafka
        self.producer = Producer({'bootstrap.servers': 'localhost:9092'})
        self.topic = 'new_gazettes' # Change this if your test topic has a different name

    def parse(self, response):
        self.log('--- Starting: Looking for initial ViewState ---')
        view_state = response.css('input[name="javax.faces.ViewState"]::attr(value)').get()
        
        if view_state:
            # Start at page 0, and tell it to start at document 0 of that page
            yield from self.download_document(current_page=0, page_index=0, view_state=view_state)

    # Note: Removed 'response' from parameters because we don't need it to build the request
    def download_document(self, current_page, page_index, view_state):
        # Calculate exact button (e.g. Page 1, doc 2 = button 52)
        absolute_index = (current_page * 50) + page_index
        exact_button = f'formResumen:dataTableResumen:{absolute_index}:btnDescargarPdf'
        
        # Add 1 to index just so console shows "1 to 50" instead of "0 to 49"
        self.log(f'--- Requesting PDF: Page {current_page}, Document {page_index + 1}/50 ---')
        
        form_data = {
            'formResumen': 'formResumen',
            'formResumen:dataTableResumen:j_idt11:filter': '',
            'formResumen:dataTableResumen:j_idt14_focus': '',
            'formResumen:dataTableResumen:j_idt14_input': '',
            'formResumen:dataTableResumen:calFechaGaceta_input': '',
            'formResumen:dataTableResumen:j_idt20:filter': '',
            exact_button: 'ui-button', 
            'javax.faces.ViewState': view_state
        }

        yield scrapy.FormRequest(
            url=self.start_urls[0],
            formdata=form_data,
            callback=self.save_pdf,
            meta={'page': current_page, 'page_index': page_index, 'view_state': view_state},
            dont_filter=True
        )

    def save_pdf(self, response):
        current_page = response.meta['page']
        page_index = response.meta['page_index']
        view_state = response.meta['view_state']
        
        # Apply the naming you requested: page enumeration and page enumeration
        destination_folder = 'documents'
        os.makedirs(destination_folder, exist_ok=True)
        file_name = f'documents/document_page_{current_page}_number_{page_index + 1}.pdf'
        path = os.path.join(file_name)
        with open(file_name, 'wb') as f:
            f.write(response.body)
            
        self.log(f'✓ SUCCESS! File saved: {file_name}')
        
        # 3. SEND MESSAGE TO KAFKA
        message = {
            "file": file_name,
            "path": path,
            "web_page": current_page,
            "status": "downloaded"
        }
        
        # Convert dictionary to JSON and send it
        self.producer.produce(self.topic, value=json.dumps(message).encode('utf-8'))
        self.producer.poll(0) # Release message queue
        
        # NEW RELAY LOGIC:
        if page_index < self.total_documents:
            # If we haven't reached document 50 yet, request next one from same page
            next_index = page_index + 1
            yield from self.download_document(current_page=current_page, page_index=next_index, view_state=view_state)
            
        elif current_page < self.total_pages - 1:
            # If we've downloaded 50 and there are more pages, change page
            next_page = current_page + 1
            self.log(f'--- All documents ready. Navigating to page {next_page} ---')
            
            pagination_data = {
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': 'formResumen:dataTableResumen',
                'javax.faces.partial.execute': 'formResumen:dataTableResumen',
                'javax.faces.partial.render': 'formResumen:dataTableResumen',
                'formResumen:dataTableResumen': 'formResumen:dataTableResumen',
                'formResumen:dataTableResumen_pagination': 'true',
                'formResumen:dataTableResumen_first': str(next_page * 50),
                'formResumen:dataTableResumen_rows': '50',
                'formResumen:dataTableResumen_encodeFeature': 'true',
                'formResumen': 'formResumen',
                'formResumen:dataTableResumen:j_idt11:filter': '',
                'formResumen:dataTableResumen:j_idt14_focus': '',
                'formResumen:dataTableResumen:j_idt14_input': '',
                'formResumen:dataTableResumen:calFechaGaceta_input': '',
                'formResumen:dataTableResumen:j_idt20:filter': '',
                'javax.faces.ViewState': view_state
            }
            
            yield scrapy.FormRequest(
                url=self.start_urls[0],
                formdata=pagination_data,
                callback=self.process_page_change,
                meta={'next_page': next_page},
                dont_filter=True
            )

    def process_page_change(self, response):
        next_page = response.meta['next_page']
        match = re.search(r'id="[^"]*ViewState[^"]*"><!\[CDATA\[(.*?)\]\]>', response.text)
        
        if match:
            new_view_state = match.group(1)
            self.log(f'Page change successful. New ViewState captured.')
            
            # Start downloading on new page, going back to start from document 0
            yield from self.download_document(current_page=next_page, page_index=0, view_state=new_view_state)
        else:
            self.log('Fatal error: Could not find ViewState in new page response.')