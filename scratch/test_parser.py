from kafka.groq_parser import parse_markdown_to_json
import json

sample_markdown = """
# Gaceta del Conreso
Proyecto de Ley Nuemro 123 de 2024. 
Autores: Senador Juan Peréz y Maria Garcai.
Este proycto busca crear una agnecia de suguridad nuclaer.
Temas: Seguridda, Energia, Regulaicion.
"""

result = parse_markdown_to_json(sample_markdown)
print(json.dumps(result, indent=4, ensure_ascii=False))
