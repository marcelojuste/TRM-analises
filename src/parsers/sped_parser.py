def parse_sped(path_file):
    sped_data_batch = []
    with open(path_file, 'r', encoding='latin-1') as file:
        for line in file:
            if line.startswith('|C100|'):
                fields = line.strip().split('|')[1:-1]

                if fields[5] != '00':
                    continue
                
                nfe = fields[8]
                tpNF = fields[1]

                sped_data_batch.append((nfe, tpNF))
    
    return sped_data_batch
