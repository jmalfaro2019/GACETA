import json

def test_merging():
    combined_result = {
        "metadatos_generales": {
            "numero_gaceta": None,
            "fecha_publicacion": None,
            "tipo_documento": None,
            "titulo_principal": "",
            "autores_o_firmantes": [],
            "palabras_clave": [],
            "resumen_ia": "",
            "contenido_limpio": ""
        },
        "detalles_especificos": {}
    }

    chunks_json = [
        {
            "metadatos_generales": {
                "numero_gaceta": "001",
                "fecha_publicacion": "2024-04-18",
                "tipo_documento": "Proyecto de Ley",
                "titulo_principal": "Ley de Seguridad Nuclear",
                "autores_o_firmantes": ["Senador A"],
                "palabras_clave": ["Nuclear"],
                "resumen_ia": "Parte 1 del resumen.",
                "contenido_limpio": "Texto limpio 1."
            },
            "detalles_especificos": {
                "numero_proyecto": "323",
                "argumentos_principales": ["Arg 1"]
            }
        },
        {
            "metadatos_generales": {
                "autores_o_firmantes": ["Senadora B"],
                "palabras_clave": ["Energia"],
                "resumen_ia": "Parte 2 del resumen.",
                "contenido_limpio": "Texto limpio 2."
            },
            "detalles_especificos": {
                "argumentos_principales": ["Arg 2"],
                "impacto_fiscal": "Bajo"
            }
        }
    ]

    for chunk_json in chunks_json:
        meta = chunk_json.get("metadatos_generales", {})
        if meta:
            if not combined_result["metadatos_generales"]["titulo_principal"]:
                combined_result["metadatos_generales"]["titulo_principal"] = meta.get("titulo_principal", "")
                combined_result["metadatos_generales"]["numero_gaceta"] = meta.get("numero_gaceta")
                combined_result["metadatos_generales"]["fecha_publicacion"] = meta.get("fecha_publicacion")
                combined_result["metadatos_generales"]["tipo_documento"] = meta.get("tipo_documento")

            combined_result["metadatos_generales"]["autores_o_firmantes"].extend(meta.get("autores_o_firmantes", []))
            combined_result["metadatos_generales"]["palabras_clave"].extend(meta.get("palabras_clave", []))
            combined_result["metadatos_generales"]["resumen_ia"] += meta.get("resumen_ia", "") + " "
            combined_result["metadatos_generales"]["contenido_limpio"] += meta.get("contenido_limpio", "") + "\n\n"

        detalles = chunk_json.get("detalles_especificos", {})
        if detalles:
            for key, value in detalles.items():
                if key not in combined_result["detalles_especificos"]:
                    combined_result["detalles_especificos"][key] = value
                else:
                    if isinstance(value, list) and isinstance(combined_result["detalles_especificos"][key], list):
                        combined_result["detalles_especificos"][key].extend(value)
                    elif isinstance(value, str) and isinstance(combined_result["detalles_especificos"][key], str):
                        if value not in combined_result["detalles_especificos"][key]:
                            combined_result["detalles_especificos"][key] += " " + value

    # Final cleanup
    meta_fin = combined_result["metadatos_generales"]
    meta_fin["titulo_principal"] = meta_fin["titulo_principal"].strip()
    meta_fin["autores_o_firmantes"] = list(set(meta_fin["autores_o_firmantes"]))
    meta_fin["palabras_clave"] = list(set(meta_fin["palabras_clave"]))
    meta_fin["resumen_ia"] = meta_fin["resumen_ia"].strip()
    meta_fin["contenido_limpio"] = meta_fin["contenido_limpio"].strip()

    print(json.dumps(combined_result, indent=4, ensure_ascii=False))

test_merging()
