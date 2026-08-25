def parse_sped(path_file):
    with open(path_file, 'r', encoding='latin-1') as file:
        for line in file:
            if line.startswith('|C100|'):
                fields = line.strip().split('|')[1:-1]

                if fields[5] != '00':
                    continue

                yield {
                    'id_nfe': fields[8],
                    'type_nfe': fields[1],
                }
