import sys

def is_null(key):
    for k in key:
        if k == "":
            return True
    return False


def add_row(row, spl):
    for i,s in enumerate(spl):
        if row[i] == "":
            row[i] = spl[i]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file> <outfile>" % sys.argv[0])
        sys.exit(-1)


    infile = open(sys.argv[1], encoding="utf-8")
    outfile = open(sys.argv[2], "w", encoding="utf-8")
    data = []
    print("id,processo_licitatorio,num_exercicio,modalidade,municipio,tipo_licitacao,data_rec_doc", file=outfile)
    spl = infile.readline().strip().split(",")
    key = (spl[0], spl[1])
    row = ["" for i in range(len(spl))]
    for line in infile:
        next_spl = line.strip().split(",")
        next_key = (next_spl[0], next_spl[1])
        if not is_null(key):
            add_row(row, spl)
            if key != next_key:
                data.append(row)
                row = ["" for i in range(len(spl))]
        spl = next_spl
        key = next_key

    if not is_null(key):
        add_row(row, spl)
        data.append(row)

    for i,spl in enumerate(data):
        print(str(i+1) + "," + ",".join(spl), file=outfile)
    infile.close()
    outfile.close()


