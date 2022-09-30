package preprocessing;

import java.util.LinkedList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class TextSegmenter {
	
	int aproxSegSize = 200;
	int minSegSize = 20;
	
	
	public TextSegmenter(int aproxSegSize, int minSegSize) {
		this.aproxSegSize = aproxSegSize;
		this.minSegSize = minSegSize;
	}

	public List<String> split(String text) {
		List<String> sentences = new LinkedList<String>();
		Pattern endOfSentence = Pattern.compile("[\\.\\?!][\s\n]+[A-Z]");
		int previousStart = 0;
		//String prevSegment = "";
		Matcher matcher = endOfSentence.matcher(text);
		StringBuilder acc = new StringBuilder();
		while(matcher.find()) {

			int start = matcher.start();
			String segment = text.substring(previousStart, start + 1);
			acc.append(segment);
			
			//System.out.println("prevSeg:" + prevSegment);
			//System.out.println("seg:" + segment);
			//System.out.println("acc:" + acc);
			//System.out.println();
			
			if(acc.length() > aproxSegSize && segment.length() > minSegSize) {
				sentences.add(acc.toString());
				acc = new StringBuilder();
			}
			//prevSegment = segment;
			previousStart = start + 1;
		}
		
		//Last sentence
		sentences.add(acc.toString() + text.substring(previousStart));
		
		return sentences;
	}

}
