import sys
import pandas

def is_null(key):
    for k in key:
        if len(k) < 4:
            return True
    return False


def add_row(row, spl):
    for i,s in enumerate(spl):
        if s != "":
            row[i] = s


NCOLS=7


def fix_spl(spl):
    if len(spl) > NCOLS:
        print("BEFORE:", spl)
        spl[6] = ",".join(spl[6:])
        print("AFTER:", spl[:7])
    return spl[:7]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file> <outfile> [nome do municipio]" % sys.argv[0])
        sys.exit(-1)

    municipio = ""
    infile = open(sys.argv[1], encoding="utf-8")
    outfile = open(sys.argv[2], "w", encoding="utf-8")
    if len(sys.argv) == 4:
        municipio = sys.argv[3]

    data = []
    print("id,processo_licitatorio,num_exercicio,modalidade,municipio,tipo_licitacao,data_rec_doc,source", file=outfile)
    spl = infile.readline().strip().split(",")
    spl = fix_spl(spl)
    key = (spl[0], spl[1])
    row = ["" for i in range(NCOLS)]
    for line in infile:
        #print(spl)
        #print(len(spl))
        next_spl = line.strip().split(",")
        next_spl = fix_spl(next_spl)
        next_key = (next_spl[0], next_spl[1])
        if not is_null(key):
            add_row(row, spl)
            if key != next_key:
                if municipio != "":
                    row[3] = municipio
                data.append(row)
                row = ["" for i in range(NCOLS)]
        spl = next_spl
        key = next_key

    if not is_null(key):
        add_row(row, spl)
        if municipio != "":
            row[3] = municipio
        data.append(row)

    for i,spl in enumerate(data):
        print(str(i+1) + "," + ",".join(spl), file=outfile)
    infile.close()
    outfile.close()


