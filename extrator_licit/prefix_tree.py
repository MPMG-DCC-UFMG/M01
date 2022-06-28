from unicodedata import normalize

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

class TreeNode:
    def __init__(self, token, terminal=None):
        self.children = {}
        self.token = token
        self.terminal = terminal
        
    #Find node containing token
    #Returns None if token not found
    def find(self, token):
        if token == self.token:
            return self
        elif token in self.children:
            return self.children[token]
        #else:
            #for node in self.children.values():
            #    res = node.find(token)
            #    if res != None:
            #        return res
        return None
    
    def add(self, seq, terminal):
        if len(seq) == 0:
            return
        tok = seq[0]
        if tok not in self.children:
            if len(seq) == 1:
                self.children[tok] = TreeNode(tok, terminal)
            else:
                self.children[tok] = TreeNode(tok)
            #print("Created node for:", tok)
        else:
            if len(seq) == 1:
                self.children[tok].terminal = terminal
            #print("Matched token:", tok)
        self.children[tok].add(seq[1:], terminal)
                

    def print_tree(self):
        print("Token:", self.token)
        print("children:", self.children.keys())
        for node in self.children.values():
            node.print_tree()


def make_dictionary(strings):
    tree = TreeNode("")
    for s in strings:
        processed = remover_acentos(s).lower()
        seq = processed.split()
        tree.add(seq, s)
    return tree


def exact_matches(sentence_tokens_low, name_tree):
    i = 0
    matches = []
    while i < len(sentence_tokens_low):
        seq = []
        node = name_tree.find(sentence_tokens_low[i])
        terminal = None
        while node != None:
            terminal = node.terminal
            seq.append(node.token)
            i += 1
            if i >= len(sentence_tokens_low):
                break
            node = node.find(sentence_tokens_low[i])
        if terminal != None: #match
            matches.append(terminal)
        if len(seq) == 0:
            i += 1 #increase pointer
    return matches


