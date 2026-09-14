SET memory_limit = '1GB';

CREATE TABLE IF NOT EXISTS nota_xml (
    nfe VARCHAR(44) PRIMARY KEY,
    tpNF INTEGER
);

CREATE TABLE IF NOT EXISTS nota_sped_ipi (
    nfe VARCHAR(44) PRIMARY KEY,
    tpNF INTEGER
);

CREATE TABLE IF NOT EXISTS nota_sped_cofins (
    nfe VARCHAR(44) PRIMARY KEY,
    tpNF INTEGER
);
