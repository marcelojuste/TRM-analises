WITH xml_nfce_daily AS (
    SELECT 
        cnpj_issuer,
        emission_date,
        nfe_model,
        SUM(total_value) AS total_value,
        COUNT(*) AS total_documents
    FROM df_xml
    WHERE nfe_model IN ('65', 'NFCe')
      AND document_status NOT IN ('Unauthorized', 'Cancelled', '02')
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
xml_nfe_daily AS (
    SELECT 
        cnpj_issuer,
        emission_date,
        nfe_model,
        SUM(total_value) AS total_value,
        COUNT(*) AS total_documents
    FROM df_xml
    WHERE nfe_model IN ('55', 'NFe')
      AND document_status NOT IN ('Unauthorized', 'Cancelled')
      AND operation_type = 'Exit'
    GROUP BY cnpj_issuer, emission_date, nfe_model
),
sintegra_50_daily AS (
    SELECT 
        cnpj_issuer,
        emission_date,
        nfe_model,
        SUM(total_value) AS total_value
    FROM df_fiscal
    WHERE nfe_model IN ('55', 'NFe')
      AND document_status NOT IN ('Unauthorized', 'Cancelled')
      AND operation_type = 'Exit'
    GROUP BY cnpj_issuer, emission_date, nfe_model
),
nfe_audit AS (
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
        'SINTEGRA_REC_50' AS fiscal_file_type,

        CASE 
            WHEN x.emission_date IS NULL THEN 'MISSING_XML'
            WHEN s.emission_date IS NULL THEN 'MISSING_SINTEGRA'
            WHEN x.total_value IS DISTINCT FROM s.total_value THEN 'VALUE_DIVERGENCE'
            ELSE 'OK'
        END AS audit_status
    FROM xml_nfe_daily x
    FULL OUTER JOIN sintegra_50_daily s 
       ON x.cnpj_issuer = s.cnpj_issuer 
      AND x.emission_date = s.emission_date
)

SELECT * FROM nfce_audit WHERE audit_status != 'OK'
UNION ALL
SELECT * FROM nfe_audit WHERE audit_status != 'OK';