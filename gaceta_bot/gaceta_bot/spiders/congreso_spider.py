import scrapy
import re
import os
import json
from confluent_kafka import Producer


class CongresoSpider(scrapy.Spider):
    name = 'congreso'
    start_urls = ['https://svrpubindc.imprenta.gov.co/senado/']
    total_paginas = 1
    total_documentos = 1
    # Creamos una carpeta para guardar los resultados
    os.makedirs("documents", exist_ok=True)
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3 
    }
    
    def __init__(self, *args, **kwargs):
        super(CongresoSpider, self).__init__(*args, **kwargs)
        # 2. Conectar a tu Kafka local
        self.producer = Producer({'bootstrap.servers': 'localhost:9092'})
        self.topic = 'gacetas_nuevas' # Cambia esto si tu tópico de prueba se llama distinto

    def parse(self, response):
        self.log('--- Iniciando: Buscando ViewState inicial ---')
        view_state = response.css('input[name="javax.faces.ViewState"]::attr(value)').get()
        
        if view_state:
            # Iniciamos en la página 0, y le decimos que empiece en el documento 0 de esa página
            yield from self.descargar_documento(pagina_actual=0, indice_en_pagina=0, view_state=view_state)

    # Nota: Le quitamos 'response' a los parámetros porque ya no lo necesitamos para armar la petición
    def descargar_documento(self, pagina_actual, indice_en_pagina, view_state):
        # Calculamos el botón exacto (ej. Página 1, doc 2 = botón 52)
        indice_absoluto = (pagina_actual * 50) + indice_en_pagina
        boton_exacto = f'formResumen:dataTableResumen:{indice_absoluto}:btnDescargarPdf'
        
        # Le sumamos 1 al índice solo para que en la consola se lea "1 al 50" en lugar de "0 al 49"
        self.log(f'--- Solicitando PDF: Página {pagina_actual}, Documento {indice_en_pagina + 1}/50 ---')
        
        datos_formulario = {
            'formResumen': 'formResumen',
            'formResumen:dataTableResumen:j_idt11:filter': '',
            'formResumen:dataTableResumen:j_idt14_focus': '',
            'formResumen:dataTableResumen:j_idt14_input': '',
            'formResumen:dataTableResumen:calFechaGaceta_input': '',
            'formResumen:dataTableResumen:j_idt20:filter': '',
            boton_exacto: 'ui-button', 
            'javax.faces.ViewState': view_state
        }

        yield scrapy.FormRequest(
            url=self.start_urls[0],
            formdata=datos_formulario,
            callback=self.guardar_pdf,
            meta={'pagina': pagina_actual, 'indice_en_pagina': indice_en_pagina, 'view_state': view_state},
            dont_filter=True
        )

    def guardar_pdf(self, response):
        pagina = response.meta['pagina']
        indice_en_pagina = response.meta['indice_en_pagina']
        view_state = response.meta['view_state']
        
        # Aplicamos el nombre que pediste: enumeración de página y enumeración en la página
        carpeta_destino = 'documents'
        os.makedirs(carpeta_destino, exist_ok=True)
        nombre_archivo = f'documents/documento_pagina_{pagina}_numero_{indice_en_pagina + 1}.pdf'
        ruta = os.path.join(nombre_archivo)
        with open(nombre_archivo, 'wb') as f:
            f.write(response.body)
            
        self.log(f'¡ÉXITO! Archivo guardado: {nombre_archivo}')
        
        # 3. ENVIAR MENSAJE A KAFKA
        mensaje = {
            "archivo": nombre_archivo,
            "ruta":ruta,
            "pagina_web": pagina,
            "estado": "descargado"
        }
        
        # Convertimos el diccionario a JSON y lo enviamos
        self.producer.produce(self.topic, value=json.dumps(mensaje).encode('utf-8'))
        self.producer.poll(0) # Libera la cola de mensajes
        
        # LA NUEVA LÓGICA DE RELEVOS:
        if indice_en_pagina < self.total_documentos:
            # Si aún no llegamos al documento 50, pedimos el siguiente de esta misma página
            siguiente_indice = indice_en_pagina + 1
            yield from self.descargar_documento(pagina_actual=pagina, indice_en_pagina=siguiente_indice, view_state=view_state)
            
        elif pagina < self.total_paginas - 1:
            # Si ya descargamos los 50 y aún quedan páginas, cambiamos de página
            siguiente_pagina = pagina + 1
            self.log(f'--- Todos los documentos listos. Navegando a la página {siguiente_pagina} ---')
            
            datos_paginacion = {
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': 'formResumen:dataTableResumen',
                'javax.faces.partial.execute': 'formResumen:dataTableResumen',
                'javax.faces.partial.render': 'formResumen:dataTableResumen',
                'formResumen:dataTableResumen': 'formResumen:dataTableResumen',
                'formResumen:dataTableResumen_pagination': 'true',
                'formResumen:dataTableResumen_first': str(siguiente_pagina * 50),
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
                formdata=datos_paginacion,
                callback=self.procesar_cambio_pagina,
                meta={'pagina_siguiente': siguiente_pagina},
                dont_filter=True
            )

    def procesar_cambio_pagina(self, response):
        pagina_siguiente = response.meta['pagina_siguiente']
        match = re.search(r'id="[^"]*ViewState[^"]*"><!\[CDATA\[(.*?)\]\]>', response.text)
        
        if match:
            nuevo_view_state = match.group(1)
            self.log(f'Cambio de página exitoso. Nuevo ViewState capturado.')
            
            # Iniciamos la descarga en la nueva página, volviendo a empezar desde el documento 0
            yield from self.descargar_documento(pagina_actual=pagina_siguiente, indice_en_pagina=0, view_state=nuevo_view_state)
        else:
            self.log('Error fatal: No pudimos encontrar el ViewState en la respuesta de la página nueva.')