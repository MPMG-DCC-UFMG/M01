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
	
//	public static void main(String[] args) {
//		
//		TextSegmenter segmenter = new TextSegmenter(200, 20);
//		
//		//String text = "Vendem-se livros. Hoje esta nublado. Vai chover em breve! Mas amanha estara ensolarado. Sera? veremos. Sera? Veremos. Lei numero tal do art. 1234. C.N.P.J. do Sr. Fulano. Oixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
//		String text = "PREFEITURA DO MUNICÍPIO DE VARGINHA.\nDepartamento de Suprimentos Rua Júlio Paulo Marcellini, nº 50   Vila Paiva   Varginha/MG   CEP: 37.018-050        Telefone (0**35) 3690-1812   FAX (0**35) 3222-9512\nE   Mail: licitacoes@varginha.mg.gov.br Edital de Licitação n.º028/2.017\nPregão Presencial n.º026/ 2.017\nPreâmbulo\n O Município de Varginha (M.G.), pessoa jurídica de direito público interno, inscrito no C.N.P.J./MF\nsob o nº 18.240.119/0001-05, com sede na Rua Júlio Paulo Marcellini, nº 50   Vila Paiva, neste ato representado por seu Prefeito,  Sr. Antonio Silva, torna público a abertura de procedimento licitatório na modalidade PREGÃO PRESENCIAL   DO TIPO MENOR PREÇO. A  presente Licitação será processada\nna conformidade do disposto na Lei Federal nº 10.520/2.002 e subsidiariamente na Lei nº 8.666/1.993 e\nsuas  alterações,  pelo  Decreto  Municipal  nº  3.311/ 2.003,  alterado  pelo  Decreto  nº  4.081,  pela  Lei\nComplementar nº 123, de 14 de dezembro de 2.006, alterada pela Lei n°. 147/2.014 e pelas disposições\ncontidas  no  ato  convocatório.";
//		for(String s : segmenter.split(text)) {
//			System.out.println(s);
//			System.out.println("===================");
//		}
//	}

}
