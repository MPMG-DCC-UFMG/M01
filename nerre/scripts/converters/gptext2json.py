import json
import sys
import spacy

# Estrutura de arvore de prefixos, eficiente para casamento exato de todas as
# palavras de um dicionario em um dado texto

class TreeNode:
    def __init__(self, token="", is_terminal=False):
        self.children = {}
        self.token = token
        self.terminal = is_terminal

    # Find node containing token
    # Returns None if token not found
    def find(self, token):
        if token == self.token:
            return self
        elif token in self.children:
            return self.children[token]
        # else:
        # for node in self.children.values():
        #    res = node.find(token)
        #    if res != None:
        #        return res
        return None

    # Adds the sequence of tokens "seq" to the vocabulary of the tree

    def add(self, seq):
        if len(seq) == 0:
            return
        tok = seq[0]
        if tok not in self.children:
            if len(seq) == 1:
                self.children[tok] = TreeNode(tok, is_terminal=True)
            else:
                self.children[tok] = TreeNode(tok, is_terminal=False)
            # print("Created node for:", tok)
        else:
            if len(seq) == 1:
                self.children[tok].terminal = True
            # print("Matched token:", tok)
        self.children[tok].add(seq[1:])

    def print_tree(self):
        print("Token:", self.token)
        print("children:", self.children.keys())
        for node in self.children.values():
            node.print_tree()

    def find_all(self, sentence_tokens_low):
        i = 0
        matches = []
        while i < len(sentence_tokens_low):
            seq = []
            node = self.find(sentence_tokens_low[i])
            terminal = False
            while node != None:
                terminal = node.terminal
                seq.append(node.token)
                i += 1
                if i >= len(sentence_tokens_low):
                    break
                node = node.find(sentence_tokens_low[i])
            if terminal:  # match
                start = i - len(seq)
                end = i
                matches.append((start, end))
            if len(seq) == 0:
                i += 1
        return matches


labels = {"[Produto ou Serviço]": "PRODUTO_OU_SERVICO",
          "[Organização]": "ORGANIZACAO",
          "[Local]": "LOCAL",
          "[Pessoa]": "PESSOA",
          "[PRODUTO_OU_SERVICO]": "PRODUTO_OU_SERVICO",
          "[PRODUTO OU SERVIÇO]": "PRODUTO_OU_SERVICO",
          "[ORGANIZACAO]": "ORGANIZACAO",
          "[LOCAL]": "LOCAL",
          "[PESSOA]": "PESSOA"
          }

def to_json(jdata):
    nlp = spacy.load("pt_core_news_sm")
    res = []
    for item in jdata:
        if item["input"] == None:
            continue
        if item["output"] == None:
            continue
        text = item["input"].strip()
        tokens = [x.text for x in nlp(text)]
        tokens_low = [x.lower() for x in tokens]
        out_lines = item["output"].split("\n")
        ents = []
        for line in out_lines:
            lin = line.strip()
            if lin.startswith("###"):
                break
            if lin.startswith("["):
                spl = lin.split(":")
                if len(spl) < 2:
                    continue
                label = spl[0].strip()
                #print(label)
                span = spl[1].strip()
                if span in labels or span.lower() == "nenhum" or span.lower() == "none" or span.lower() == "nada":
                    continue
                if label not in labels:
                    continue
                print(span)
                ents.append( (labels[label], span) )

        entities = []
        for label, span in ents:
            matcher = TreeNode()
            seq = span.lower().split()
            matcher.add(seq)
            matches = matcher.find_all(tokens_low)

            for start, end in matches:
                entities.append({"start": start, "end": end, "type": label})
        res.append({"tokens": tokens, "entities": entities, "relations": []})
    return res



def txt2json(data):
    res = []
    lines = data.split("\n")
    i = 0
    answer = None
    for line in lines:
        lin = line.strip()
        if lin == "":
            continue
        #print(lin)
        if lin.startswith("[Text]:"):
            if answer != None:
                dic = {"input": text, "output": answer}
                #print(dic)
                res.append(dic)
            text = lin[8:]
            answer = ""
        else: #Continuacao do texto ou da resposta
            if lin.startswith("["):
                if not lin.startswith("[ID]"):
                    answer += (lin + "\n")
            else:
                text += (lin + "\n")

    res.append({"input": text, "output": answer})
    return to_json(res)




if __name__ == "__main__":

    infile = open(sys.argv[1], encoding="utf-8")
    output = open(sys.argv[2], "w", encoding="utf-8")

    if infile.name.endswith(".json"):
        data = json.load(infile)
        res = to_json(data)
    else:
        data = infile.read()
        res = txt2json(data)

    json.dump(res, output, indent=4)
    infile.close()
    output.close()

