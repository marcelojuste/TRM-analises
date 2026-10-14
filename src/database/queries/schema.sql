CREATE TABLE IF NOT EXISTS xml_documents (
    access_key      VARCHAR(44) PRIMARY KEY,
    cnpj_emit       VARCHAR(14) NOT NULL,
    total_value     BIGINT NOT NULL,
    emission_date   VARCHAR(10) NOT NULL,
    nfe_model       UTINYINT NOT NULL,
    document_status VARCHAR(2) NOT NULL
);

CREATE TABLE IF NOT EXISTS sped_documents (
    access_key      VARCHAR(44) NOT NULL,
    cnpj_emit       VARCHAR(14) NOT NULL,
    total_value     BIGINT NOT NULL,
    emission_date   VARCHAR(10) NOT NULL,
    nfe_model       UTINYINT NOT NULL,
    document_status VARCHAR(2) NOT NULL,
    sped_type       VARCHAR(12) NOT NULL,
    
    PRIMARY KEY (access_key, sped_type)
);

CREATE INDEX IF NOT EXISTS idx_xml_status ON xml_documents(document_status);
CREATE INDEX IF NOT EXISTS idx_sped_status ON sped_documents(document_status);