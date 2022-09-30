package postprocessing;

import java.text.Normalizer;
import java.util.HashSet;
import java.util.Set;

import edu.stanford.nlp.util.Triple;
import preprocessing.TextCleaner;

public class PostProcessor {

	private static Set<String> LOCAL_PREFIX = new HashSet<String>() {
	    private static final long serialVersionUID = 1L;
	    {
	        add("rua");
	        add("r");
	        add("r.");
	        add("avenida");
	        add("av");
	        add("av.");
	        add("ave");
	        add("ave.");
	        add("bairro");
	        add("rodovia");
	        add("jd");
	        add("jd.");
	        add("praça");
	        add("ilha");
	        add("travessia");
	    }
	};
	
	public static Triple<String, Integer, Integer> correct(Triple<String, Integer, Integer> triple, String text) {
		int st = triple.second - 15;
		int begin = Math.max(0, st);
		String[] prefix = text.substring(begin, triple.second).toLowerCase().split("\s+");
		if(prefix.length == 0)
			return triple;
		String lastWord = prefix[prefix.length - 1];
		if(LOCAL_PREFIX.contains(lastWord))
			return new Triple<String, Integer, Integer>("LOCAL", triple.second - lastWord.length() - 1, triple.third);
		return triple;
	}

	public static void main(String[] args) {
		
		String text = "";
		System.out.println(TextCleaner.cleanText(Normalizer.normalize(text, Normalizer.Form.NFKD)));
		Triple<String, Integer, Integer> label = PostProcessor.correct(new Triple<String, Integer, Integer>("PESSOA", 68, 90), text);
		System.out.println(label.first + ":" + text.substring(label.second, label.third));
	}

}
