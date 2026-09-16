CREATE TABLE IF NOT EXISTS xml_documents (
    acces_key VARCHAR(44) PRIMARY KEY,
    total_value BIGINT NOT NULL,
    emission_date DATE NOT NULL,
    nf_type UTINYINT NOT NULL,
);

CREATE TABLE IF NOT EXISTS sped_documents (
    access_key VARCHAR(44),
    sped_type VARCHAR(12),
    situation_code VARCHAR(2),
    total_value BIGINT,
    PRIMARY KEY (access_key, sped_type)
);
