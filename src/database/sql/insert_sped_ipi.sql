INSERT INTO nota_sped_ipi (nfe, tpNF)
VALUES (?, ?)
ON CONFLICT (nfe) DO UPDATE SET tpNF = EXCLUDED.tpNF;