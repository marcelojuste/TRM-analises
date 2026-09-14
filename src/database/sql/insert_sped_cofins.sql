INSERT INTO nota_sped_cofins (nfe, tpNF)
VALUES (?, ?)
ON CONFLICT (nfe) DO UPDATE SET tpNF = EXCLUDED.tpNF;