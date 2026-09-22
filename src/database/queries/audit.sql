SELECT 
    COALESCE(x.access_key, s.access_key) AS chave_acesso,
    COALESCE(x.cnpj_emit, s.cnpj_emit) AS cnpj_emitente,

    x.total_value AS valor_xml_centavos,
    x.emission_date AS data_emissao_xml,
    x.document_status AS status_xml,
        
    s.total_value AS valor_sped_centavos,
    s.emission_date AS data_emissao_sped,
    s.document_status AS status_sped,
    s.sped_type AS tipo_sped,

CASE 
    WHEN x.access_key IS NULL THEN 'XML_AUSENTE'
    WHEN s.access_key IS NULL THEN 'SPED_AUSENTE'
    WHEN x.total_value != s.total_value THEN 'DIVERGENCIA_VALOR'
    WHEN x.document_status != s.document_status THEN 'DIVERGENCIA_STATUS'
    WHEN x.emission_date != s.emission_date THEN 'DIVERGENCIA_DATA'
    ELSE 'OK'
END AS status_auditoria

FROM xml_documents x
FULL OUTER JOIN sped_documents s 
    ON x.access_key = s.access_key

WHERE x.access_key IS NULL 
    OR s.access_key IS NULL 
    OR x.total_value != s.total_value 
    OR x.document_status != s.document_status 
    OR x.emission_date != s.emission_date

ORDER BY cnpj_emitente, chave_acesso
