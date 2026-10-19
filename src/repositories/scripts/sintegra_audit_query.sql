WITH xml_nfce_daily AS (
    SELECT 
        cnpj_issuer,
        emission_date,
        nfe_model,
        SUM(total_value) AS total_value,
        COUNT(*) AS total_documents
    FROM df_xml
    WHERE nfe_model IN ('65', 'NFCe')
      AND document_status NOT IN ('Unauthorized', 'Cancelled', '02', 'Nao autorizada')
    GROUP BY cnpj_issuer, emission_date, nfe_model
),
sintegra_61_daily AS (
    SELECT 
        cnpj_issuer,
        emission_date,
        nfe_model,
        SUM(total_value) AS total_value
    FROM df_fiscal
    WHERE nfe_model IN ('65', 'NFCe')
    GROUP BY cnpj_issuer, emission_date, nfe_model
),
nfce_audit AS (
    SELECT 
        NULL AS access_key,
        COALESCE(x.nfe_model, s.nfe_model) AS nfe_model,
        COALESCE(x.cnpj_issuer, s.cnpj_issuer) AS cnpj_issuer,
        'TOTAL_DIARIO' AS document_number,

        x.total_value AS xml_value_cents,
        x.emission_date AS xml_emission_date,
        'Authorized' AS xml_status,

        s.total_value AS fiscal_value_cents,
        s.emission_date AS fiscal_emission_date,
        'Authorized' AS fiscal_status,
        'SINTEGRA_REC_61' AS fiscal_file_type,

        CASE 
            WHEN x.emission_date IS NULL THEN 'MISSING_XML'
            WHEN s.emission_date IS NULL THEN 'MISSING_SINTEGRA'
            WHEN x.total_value IS DISTINCT FROM s.total_value THEN 'VALUE_DIVERGENCE'
            ELSE 'OK'
        END AS audit_status
    FROM xml_nfce_daily x
    FULL OUTER JOIN sintegra_61_daily s 
       ON x.cnpj_issuer = s.cnpj_issuer 
      AND x.emission_date = s.emission_date
),
xml_nfe_filtered AS (
    SELECT 
        access_key, 
        cnpj_issuer, 
        total_value, 
        emission_date, 
        nfe_model, 
        document_status, 
        CAST(document_number AS VARCHAR) AS document_number
    FROM df_xml
    WHERE nfe_model IN ('55', 'NFe')
      AND document_status NOT IN ('Unauthorized', 'Cancelled', '02', 'Nao autorizada')
),
sintegra_50_filtered AS (
    SELECT 
        cnpj_issuer, 
        total_value, 
        emission_date, 
        nfe_model, 
        document_status, 
        CAST(document_number AS VARCHAR) AS document_number
    FROM df_fiscal
    WHERE nfe_model IN ('55', 'NFe')
      AND document_status NOT IN ('Unauthorized', 'Cancelled', '02', 'Nao autorizada')
),
nfe_audit AS (
    SELECT 
        x.access_key,
        COALESCE(x.nfe_model, s.nfe_model) AS nfe_model,
        COALESCE(x.cnpj_issuer, s.cnpj_issuer) AS cnpj_issuer,
        COALESCE(x.document_number, s.document_number) AS document_number,

        x.total_value AS xml_value_cents,
        x.emission_date AS xml_emission_date,
        x.document_status AS xml_status,

        s.total_value AS fiscal_value_cents,
        s.emission_date AS fiscal_emission_date,
        s.document_status AS fiscal_status,
        'SINTEGRA_REC_50' AS fiscal_file_type,

        CASE 
            WHEN x.document_number IS NULL THEN 'MISSING_XML'
            WHEN s.document_number IS NULL THEN 'MISSING_SINTEGRA'
            WHEN x.total_value IS DISTINCT FROM s.total_value THEN 'VALUE_DIVERGENCE'
            WHEN x.document_status IS DISTINCT FROM s.document_status THEN 'STATUS_DIVERGENCE'
            ELSE 'OK'
        END AS audit_status
    FROM xml_nfe_filtered x
    FULL OUTER JOIN sintegra_50_filtered s 
       ON x.cnpj_issuer = s.cnpj_issuer 
      AND x.emission_date = s.emission_date
      AND x.document_number = s.document_number
)

SELECT * FROM nfce_audit WHERE audit_status != 'OK'
UNION ALL
SELECT * FROM nfe_audit WHERE audit_status != 'OK';