WITH

-- ============================================================
-- 1. NORMALIZAÇÃO DAS FONTES
--    Garante uma única ocorrência por NFe em cada tabela
-- ============================================================

xml AS (
    SELECT
        nfe,
        MAX(tpNF) AS tpNF,
        COUNT(DISTINCT tpNF) AS tpnf_count
    FROM nota_xml
    GROUP BY nfe
),

sped_ipi AS (
    SELECT
        nfe,
        MAX(tpNF) AS tpNF,
        COUNT(DISTINCT tpNF) AS tpnf_count
    FROM nota_sped_ipi
    GROUP BY nfe
),

sped_cofins AS (
    SELECT
        nfe,
        MAX(tpNF) AS tpNF,
        COUNT(DISTINCT tpNF) AS tpnf_count
    FROM nota_sped_cofins
    GROUP BY nfe
),


-- ============================================================
-- 2. TODAS AS CHAVES
-- ============================================================

all_keys AS (
    SELECT DISTINCT nfe
    FROM (
        SELECT nfe FROM xml

        UNION ALL

        SELECT nfe FROM sped_ipi

        UNION ALL

        SELECT nfe FROM sped_cofins
    )
),


-- ============================================================
-- 3. CONSOLIDAÇÃO
-- ============================================================

base AS (
    SELECT

        c.nfe AS access_key,

        -- Prioridade:
        -- XML > IPI > COFINS
        COALESCE(
            x.tpNF,
            i.tpNF,
            cof.tpNF
        ) AS tpNF,

        x.nfe AS nfe_xml,
        i.nfe AS nfe_sped_ipi,
        cof.nfe AS nfe_sped_cofins,

        -- Detecta divergência de tpNF dentro da própria fonte
        COALESCE(x.tpnf_count, 0)
        + COALESCE(i.tpnf_count, 0)
        + COALESCE(cof.tpnf_count, 0) AS total_tpnf_variations,

        -- Detecta se alguma fonte possui mais de um tpNF
        CASE
            WHEN COALESCE(x.tpnf_count, 0) > 1
              OR COALESCE(i.tpnf_count, 0) > 1
              OR COALESCE(cof.tpnf_count, 0) > 1
            THEN TRUE
            ELSE FALSE
        END AS source_tpnf_discrepancy

    FROM all_keys c

    LEFT JOIN xml x
        ON c.nfe = x.nfe

    LEFT JOIN sped_ipi i
        ON c.nfe = i.nfe

    LEFT JOIN sped_cofins cof
        ON c.nfe = cof.nfe
),


-- ============================================================
-- 4. AUDITORIA
-- ============================================================

audit AS (
    SELECT

        access_key,

        tpNF,

        CASE
            WHEN tpNF = 1 THEN 'SAIDA'
            WHEN tpNF = 0 THEN 'ENTRADA'
            ELSE 'NAO IDENTIFICADO'
        END AS invoice_direction,

        xml_present,
        sped_ipi_present,
        sped_cofins_present,

        CASE

            -- =================================================
            -- 1. DIVERGÊNCIA INTERNA DE tpNF
            -- =================================================

            WHEN source_tpnf_discrepancy
            THEN
                'ERRO: NFe possui tpNF divergente dentro da mesma fonte'


            -- =================================================
            -- 2. XML AUSENTE
            -- =================================================

            WHEN NOT xml_present
                 AND (
                     sped_ipi_present
                     OR sped_cofins_present
                 )
            THEN
                'ERRO DE GUARDA: Nota declarada no SPED, mas XML nao encontrado na pasta'


            -- =================================================
            -- 3. SAÍDAS / VENDAS
            -- =================================================

            WHEN tpNF = 1
                 AND NOT sped_ipi_present
                 AND NOT sped_cofins_present
            THEN
                'ERRO CRITICO: Venda omitida em AMBOS os SPEDs'

            WHEN tpNF = 1
                 AND NOT sped_ipi_present
            THEN
                'ERRO CRITICO: Venda omitida no SPED IPI'

            WHEN tpNF = 1
                 AND NOT sped_cofins_present
            THEN
                'ERRO CRITICO: Venda omitida no SPED COFINS'


            -- =================================================
            -- 4. ENTRADAS / COMPRAS
            -- =================================================

            WHEN tpNF = 0
                 AND NOT sped_ipi_present
                 AND NOT sped_cofins_present
            THEN
                'ERRO: Compra omitida em AMBOS os SPEDs'

            WHEN tpNF = 0
                 AND NOT sped_ipi_present
            THEN
                'ERRO: Compra omitida no SPED IPI'

            WHEN tpNF = 0
                 AND NOT sped_cofins_present
            THEN
                'ALERTA: Compra nao declarada no SPED COFINS (Verificar Lucro Presumido)'


            -- =================================================
            -- 5. tpNF DESCONHECIDO
            -- =================================================

            WHEN tpNF IS NULL
            THEN
                'ERRO: tpNF nao identificado'


            -- =================================================
            -- 6. OK
            -- =================================================

            ELSE
                'OK'

        END AS audit_status

    FROM (
        SELECT

            access_key,
            tpNF,

            nfe_xml IS NOT NULL AS xml_present,
            nfe_sped_ipi IS NOT NULL AS sped_ipi_present,
            nfe_sped_cofins IS NOT NULL AS sped_cofins_present,

            source_tpnf_discrepancy

        FROM base
    )
)


-- ============================================================
-- 5. RESULTADO FINAL
-- ============================================================

SELECT
    access_key,
    tpNF,
    invoice_direction,
    xml_present,
    sped_ipi_present,
    sped_cofins_present,
    audit_status

FROM audit

WHERE audit_status <> 'OK'

ORDER BY
    tpNF DESC,
    audit_status,
    access_key;
