import java.io.IOException;
import java.util.LinkedList;
import java.util.List;

import edu.stanford.nlp.ie.crf.CRFClassifier;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.sequences.FeatureFactory;

public class FeaturePrinter {
	
	static CRFClassifier<CoreLabel> classifier;

	public static void main(String[] args) throws ClassCastException, ClassNotFoundException, IOException {
		
		String serializedClassifier = "models/lener_model.ser.gz";
		classifier = CRFClassifier.getClassifier(serializedClassifier);
		List<List<CoreLabel>> answer = classifier.classify("O Brasil passou vergonha na ONU novamente. Meu nome é Fabiano Muniz.");
		List<FeatureFactory<CoreLabel>> featfacs = classifier.featureFactories;
		
		for(FeatureFactory<CoreLabel> featfac : featfacs) {
			System.out.println();
		}
	}
	
	
	public List<CoreLabel> toList(List<List<CoreLabel>> answer) {
		List<CoreLabel> res = new LinkedList<CoreLabel>();
		
		for(List<CoreLabel> sentence: answer) {
			for (CoreLabel word : sentence) {
				res.add(word);
			}
		}
		return res;
	}

}
