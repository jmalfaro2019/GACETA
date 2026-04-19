import scrapy
import re
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


class CongresoSpider(scrapy.Spider):
    name = 'congreso'
    start_urls = ['https://svrpubindc.imprenta.gov.co/senado/']
    total_pages = 20
    total_documents = 50
    os.makedirs("documents", exist_ok=True)
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3
    }

    def __init__(self, *args, **kwargs):
        super(CongresoSpider, self).__init__(*args, **kwargs)
        # Configuración de API y Seguridad
        self.api_url = os.getenv('NEXT_PUBLIC_API_URL', 'http://localhost:8000/api/v1')
        self.api_key = os.getenv('API_SECRET_KEY', 'super-secret-default-key')
        
        # Ya no necesitamos conexión directa a RabbitMQ desde la araña
        self.connection = None
        self.channel = None
        
        self.queue = 'new_gazettes'
        self.log(f"Spider initialized. Target API: {self.api_url}")

    def document_exists_in_db(self, title):
        """Checks if a document with this title already exists in the database."""
        try:
            # We search for the exact title
            response = requests.get(f"{self.api_url}/documents/search?q={title}")
            if response.status_code == 200:
                results = response.json()
                # If there's an exact match in the titles
                return any(doc['titre'].lower() == title.lower() for doc in results)
        except Exception as e:
            self.log(f"Error checking document existence: {e}")
        return False

    def upload_to_api(self, file_path, file_name):
        """Uploads the PDF to the backend API."""
        url = f"{self.api_url}/documents/upload"
        headers = {"X-API-Key": self.api_key}
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/pdf')}
                response = requests.post(url, headers=headers, files=files)
                
            if response.status_code == 200:
                self.log(f"Successfully uploaded {file_name} to API.")
                return True
            else:
                self.log(f"Failed to upload {file_name}. Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log(f"Error during API upload: {e}")
        return False

    def parse(self, response):
        self.log('Starting: Looking for initial ViewState')
        view_state = response.css('input[name="javax.faces.ViewState"]::attr(value)').get()

        if view_state:
            yield from self.download_document(current_page=0, page_index=0, view_state=view_state)

    def download_document(self, current_page, page_index, view_state):
        absolute_index = (current_page * 50) + page_index
        exact_button = f'formResumen:dataTableResumen:{absolute_index}:btnDescargarPdf'

        self.log(f'Requesting PDF: Page {current_page}, Document {page_index + 1}/50')
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

        destination_folder = 'documents'
        os.makedirs(destination_folder, exist_ok=True)
        file_name = f'document_page_{current_page}_number_{page_index + 1}.pdf'
        file_path = os.path.join(destination_folder, file_name)
        
        # Incremental check: Skip if already in DB
        if self.document_exists_in_db(file_name):
            self.log(f"SKIPPING: {file_name} already exists in database.")
        else:
            with open(file_path, 'wb') as f:
                f.write(response.body)
            self.log(f'SUCCESS! File saved: {file_name}')

            # 2. Upload to API (triggers the rest of the pipeline)
            self.upload_to_api(file_path, file_name)

        if page_index < self.total_documents:
            next_index = page_index + 1
            yield from self.download_document(current_page=current_page, page_index=next_index, view_state=view_state)

        elif current_page < self.total_pages - 1:
            next_page = current_page + 1
            self.log(f'All documents ready. Navigating to page {next_page}')

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

            yield from self.download_document(current_page=next_page, page_index=0, view_state=new_view_state)
        else:
            self.log('Fatal error: Could not find ViewState in new page response.')