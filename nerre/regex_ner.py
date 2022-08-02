import sys
import re
from pycpfcnpj import cpfcnpj

class RegexNER:
    def __init__(self, regex_filename):
        self.regex_filename = regex_filename
        self.patterns = self.load_regex_file()

    def load_regex_file(self):
        patterns = []
        infile = open(self.regex_filename, encoding="utf-8")
        for line in infile:
            lin = line.strip()
            if lin.startswith("#"):
                continue
            spl = lin.strip().split("\t")
            #print(spl)
            if len(spl) < 2:
                continue
            name = spl[0]
            expr = spl[1]
            patterns.append( (name, re.compile(expr)) )
        infile.close()
        #for pattern in patterns:
        #    print(pattern[0])
        return patterns


    def additional_validation(self, ent_type, span):
        if ent_type == "CPF" or ent_type == "CNPJ":
            return cpfcnpj.validate(span)
        return True

    def ner(self, text):
        ents = []
        for ent_type, pattern in self.patterns:
            for match in pattern.finditer(text):
                start, end = match.span()
                span = text[start:end]
                if self.additional_validation(ent_type, span):
                    ents.append( (start, end, ent_type) )
        return ents

