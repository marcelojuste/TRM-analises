def parse_sped(path_file):
    with open(path_file, 'r', encoding='latin-1') as file:
        for line in file:
            if line.startswith('|C100|'):
                fields = line.strip().split('|')[1:-1]

                if fields[5] != '00':
                    continue
                
                nfe = fields[8]
                tpNF = fields[1]

                yield (
                    nfe,
                    tpNF
                )
