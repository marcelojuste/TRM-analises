SET memory_limit = '1GB';

CREATE TABLE nota_xml (
    nfe VARCHAR(44) PRIMARY KEY,
    tpNF INTEGER
);

CREATE TABLE nota_sped_ipi (
    nfe VARCHAR(44) PRIMARY KEY,
    tpNF INTEGER
);

CREATE TABLE nota_sped_cofins (
    nfe VARCHAR(44) PRIMARY KEY,
    tpNF INTEGER
);