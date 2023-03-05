
def load_config(filename="config.txt"):
    configs = {}
    with open(filename) as infile:
        for line in infile:
            if "=" in line:
                spl = line.strip().split("=")
                configs[spl[0].strip()] = spl[1].strip()
    return configs
