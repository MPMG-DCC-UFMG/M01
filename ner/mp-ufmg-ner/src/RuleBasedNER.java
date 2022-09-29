import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.collections4.map.HashedMap;

import cpfcnpj.CpfCnpjUtils;
import edu.stanford.nlp.util.Triple;
public class RuleBasedNER {

	Map<String, Pattern> rules;
	
	public RuleBasedNER(String regexFileName) throws IOException {
		rules = new HashedMap<String, Pattern>();
		BufferedReader reader = new BufferedReader(new FileReader(regexFileName));
		String line;
		while((line = reader.readLine()) != null) {
			if(line.trim().startsWith("#"))
				continue;
			if(line.trim().length() == 0)
				continue;
			String[] spl = line.split("\t");
			if(spl.length > 1)
				rules.put(spl[0], Pattern.compile(spl[1]));
		}
		reader.close();
	}
	
	public List<Triple<String, Integer, Integer>> ner(String text) {
		
		List<Triple<String, Integer, Integer>> res = new LinkedList<Triple<String, Integer, Integer>>();
		for(Entry<String, Pattern> entry : rules.entrySet()) {
			Matcher matcher = entry.getValue().matcher(text);
			while(matcher.find()) {
				String ent = text.substring(matcher.start(), matcher.end());
				if(additionalValidation(entry.getKey(), ent))
					res.add(new Triple<String, Integer, Integer>(entry.getKey(), matcher.start(), matcher.end()));
			}
		}
		return res;
	}

	private boolean additionalValidation(String entType, String ent) {
		if(entType.equals("CPF"))
			return CpfCnpjUtils.isValidCPF(ent);
		else if(entType.equals("CNPJ"))
			return CpfCnpjUtils.isValidCNPJ(ent);
		return true;
	}

}
