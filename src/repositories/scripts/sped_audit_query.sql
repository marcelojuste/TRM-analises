WITH xml_filtered AS (
    SELECT 
        access_key, 
        cnpj_issuer, 
        total_value, 
        emission_date, 
        nfe_model, 
        document_status, 
        document_number
    FROM df_xml
    WHERE document_status NOT IN ('Unauthorized', 'Cancelled', '02', 'Nao autorizada')
),
sped_filtered AS (
    SELECT 
        access_key, 
        cnpj_issuer, 
        total_value, 
        emission_date, 
        nfe_model, 
        document_status, 
        document_number, 
        sped_type
    FROM df_fiscal
    WHERE document_status NOT IN ('Unauthorized', 'Cancelled', '02', 'Nao autorizada')
)
SELECT 
    COALESCE(x.access_key, s.access_key) AS access_key,
    COALESCE(x.nfe_model, s.nfe_model) AS nfe_model,
    COALESCE(x.cnpj_issuer, s.cnpj_issuer) AS cnpj_issuer,
    COALESCE(x.document_number, s.document_number) AS document_number,

    x.total_value AS xml_value_cents,
    x.emission_date AS xml_emission_date,
    x.document_status AS xml_status,
        
    s.total_value AS fiscal_value_cents,
    s.emission_date AS fiscal_emission_date,
    s.document_status AS fiscal_status,
    s.sped_type AS fiscal_file_type,

    CASE 
        WHEN x.access_key IS NULL THEN 'MISSING_XML'
        WHEN s.access_key IS NULL THEN 'MISSING_SPED'
        WHEN x.total_value IS DISTINCT FROM s.total_value THEN 'VALUE_DIVERGENCE'
        WHEN x.document_status IS DISTINCT FROM s.document_status THEN 'STATUS_DIVERGENCE'
        WHEN x.emission_date IS DISTINCT FROM s.emission_date THEN 'DATE_DIVERGENCE'
        ELSE 'OK'
    END AS audit_status

FROM xml_filtered x
FULL OUTER JOIN sped_filtered s ON x.access_key = s.access_key

WHERE x.access_key IS NULL 
   OR s.access_key IS NULL 
   OR x.total_value IS DISTINCT FROM s.total_value 
   OR x.document_status IS DISTINCT FROM s.document_status 
   OR x.emission_date IS DISTINCT FROM s.emission_date;