package preprocessing;

public class TextCleaner {
	
	private static final String[][] replaceList = { {"\r", ""},
			                                        {"-\n", ""}, //Trata separacao de palavras por hifen seguido de nova linha
			                                        {" / ", "/"},
			                                        //{" - ", "-"},
                                                    {"\u00ba.", "\u00ba "}, 
                                                    {"\u00aa.", "\u00aa "} };

	//Remocao de caracteres invalidos
	public static String cleanText(String text) {
		
	    for(String[] repl : replaceList)
	    	text = text.replaceAll(repl[0], repl[1]);
		
	    String res = "";
		for(int i = 0; i < text.length(); i++) {
			char c = text.charAt(i);
			if ( (c >= '\u0009' && c <= '\u007E') || (c >= '\u00A1' && c <= '\u00FF'))// || c == '\n')
				res += c;
			else
				res += ' ';
		}	    	    		
    	return res;
	}
	
	public static String removeNL(String text) {
		return text.replaceAll("\n", "");
	}

}
