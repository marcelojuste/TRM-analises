CREATE TABLE IF NOT EXISTS xml_documents (
    access_key VARCHAR(44) PRIMARY KEY,
    cnpj_emit VARCHAR(14),
    total_value BIGINT NOT NULL,
    emission_date DATE NOT NULL,
    nf_type UTINYINT NOT NULL,
    situation_code VARCHAR(2) DEFAULT '00'
);

CREATE TABLE IF NOT EXISTS sped_documents (
    access_key VARCHAR(44) NOT NULL,
    cnpj_emit VARCHAR(14),
    total_value BIGINT,
    emission_date DATE NOT NULL,
    situation_code VARCHAR(2) NOT NULL,
    sped_type VARCHAR(12) NOT NULL,
    PRIMARY KEY (access_key, sped_type)
);
