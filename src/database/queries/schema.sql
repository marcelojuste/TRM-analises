CREATE TABLE IF NOT EXISTS xml_documents (
    access_key VARCHAR(44) PRIMARY KEY,
    total_value BIGINT
);

CREATE TABLE IF NOT EXISTS sped_documents (
    access_key VARCHAR(44),
    total_value BIGINT,
    sped_type VARCHAR(12),
    situation_code VARCHAR(2),
    PRIMARY KEY (access_key, sped_type)
);
