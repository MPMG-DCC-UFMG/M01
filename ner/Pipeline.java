
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.sql.Timestamp;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.tika.exception.TikaException;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.parser.ParseContext;
import org.apache.tika.parser.html.HtmlParser;
import org.apache.tika.sax.BodyContentHandler;
import org.json.JSONObject;
import org.xml.sax.SAXException;

import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.CRFClassifier;
import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.util.Pair;
import edu.stanford.nlp.util.Triple;
import postprocessing.PostProcessor;
import preprocessing.TextCleaner;
import preprocessing.TextSegmenter;

public class Pipeline {
	
	static AbstractSequenceClassifier<CoreLabel> classifier;
	static RuleBasedNER regexNER;
	static boolean printSegmented = false;
	static boolean removeNL = false;
	static boolean executeServer = false;
	//static boolean printConll = true;

    static List<Pair<File, String>> taskList;
    static TextSegmenter segmenter;
	
	public static void main(String[] args) throws Exception {

		Properties prop = new Properties();
		prop.load(new InputStreamReader(new FileInputStream("config.txt")));
		
		String regexFile = prop.getProperty("regexFile");
		int aproxSegSize = Integer.parseInt(prop.getProperty("aproxSegmentSize"));
		int minSegSize = Integer.parseInt(prop.getProperty("minSegmentSize"));
		String serializedClassifier = prop.getProperty("model");
		printSegmented = Boolean.parseBoolean(prop.getProperty("segmented"));
		removeNL = Boolean.parseBoolean(prop.getProperty("removeNewLines"));
		executeServer = (args.length == 0);
		
		//printConll = Boolean.parseBoolean(prop.getProperty("printConllFormat"));
		segmenter = new TextSegmenter(aproxSegSize, minSegSize);
		
		//String serializedClassifier = "models/lener_model.ser.gz";

		classifier = CRFClassifier.getClassifier(serializedClassifier);
		regexNER = new RuleBasedNER(regexFile);
		
		if(executeServer) {
		    processRequests();
		}
		
//		String text;
//		if(args[0].equals("-str")) {
//			text = args[1];
//			run(TextCleaner.cleanText(text), System.out);
//			return;
//		}

		String indir = args[0];
		String outdir = args[1];
		System.out.println("Input File or Directory: " + indir);
		System.out.println("Ouput File or Directory: " + outdir);
		System.out.println("NER model: " + serializedClassifier);

		File dir = new File(indir);

		if(dir.isFile()) {
			System.out.println("Input is file.");
			run(dir, outdir);
			return;
		}

		int nThreads = Math.floorDiv(Runtime.getRuntime().availableProcessors(),  2); 
		//if(args.length == 3)
		//	nThreads = Integer.parseInt(args[2]);

        taskList = new LinkedList<Pair<File,String>>();
        allocate(dir, outdir); //Updates taskList
        
        System.out.println("#Threads=" + nThreads);
        
        ExecutorService service = Executors.newFixedThreadPool(nThreads);
        for(Pair<File, String> p : taskList) {
        	service.execute(() -> run(p.first(), p.second()));
        }
        
        service.shutdown();
        //service.awaitTermination(1, TimeUnit.MINUTES);
		//run(dir, outdir);

	}
	
	
	public static void processRequests() throws IOException {
		Properties prop = new Properties();
		prop.load(new InputStreamReader(new FileInputStream("service_config.txt")));
		int port = Integer.parseInt(prop.getProperty("port"));
		int nThreads = Math.floorDiv(Runtime.getRuntime().availableProcessors(),  2); 
		ExecutorService serverThreads = Executors.newFixedThreadPool(nThreads);
		System.out.println("Starting server on port " + port );
		@SuppressWarnings("resource")
		ServerSocket ssocket = new ServerSocket(port);
		
		while (true) {
			Socket csocket = ssocket.accept();
			serverThreads.execute(() -> {
				try {
			            answerRequest(csocket);
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			});
	    }
	}


	public static void answerRequest(Socket csocket) throws IOException {
		System.out.println("Connected");
		BufferedReader fromClient = new BufferedReader(new InputStreamReader(csocket.getInputStream()));
		PrintStream toClient = new PrintStream(csocket.getOutputStream());
		String line = fromClient.readLine().trim();
		JSONObject json = new JSONObject(line);
		System.out.println(json.toString());
		if(json.has("input"))
		{
		    String input = (String) json.get("input");
		    String output = (String) json.get("output");
		    run(new File(input), output);
		    toClient.println("FINISHED");
		}
		else
		{
			String text = json.getString("text");
			JSONObject res = classify(TextCleaner.cleanText(text));
			toClient.println(res.toString(4));
		}
		csocket.close();
	}
	
	
	public static void answerStringRequest(Socket csocket) throws IOException {
		System.out.println("Connected");
		BufferedReader fromClient = new BufferedReader(new InputStreamReader(csocket.getInputStream()));
		PrintStream toClient = new PrintStream(csocket.getOutputStream());
		String line = "";
		String text = "";
		while (!(line = fromClient.readLine()).trim().equals("[EOF]")) {
		    text += "\n" + line.trim();	
		}
		System.out.println("Processing text:" + text);
		JSONObject res = classify(TextCleaner.cleanText(text));
		toClient.println(res.toString(4));
	    csocket.close();
	}
	
	
	public static void writeAnswerInFile(List<Triple<String, Integer, Integer>> answer, String srcFileName, String text, PrintStream outfile) throws FileNotFoundException {
		
		JSONObject json = formatJson(answer, srcFileName, text);
		outfile.print(json.toString(4));
		outfile.close();
	}


	public static JSONObject formatJson(List<Triple<String, Integer, Integer>> answer, String srcFileName,
			String text) {
		//PrintStream outfile = new PrintStream(outFileName);

		Map<String, Object> res =  new HashMap<String, Object>();
		res.put("file", srcFileName);
		res.put("text", text);
		Date date = new Date();
		Timestamp time = new Timestamp(date.getTime());
		res.put("timestamp", time.toString());
		
		List<Map<String, Object>> ents = new LinkedList<Map<String, Object>>();
		
		//End of list marker
		answer.add(new Triple<String, Integer, Integer>("", -1, -1));
		
		Iterator<Triple<String, Integer, Integer>> it = answer.iterator();
		
		Triple<String, Integer, Integer> item = it.next();
		String currentEnt = "";
		
		while(item.second() != -1) {
			//System.out.println(item + ": " + text.substring(item.second(), item.third()));
			String label = item.first();
			int start = item.second();
			int end = item.third();
			
			if(label.charAt(1) == '-') {
				currentEnt = label.substring(2);
			}
			else {
				currentEnt = label;
				item = it.next();
			}
			
			if(label.startsWith("B-"))
				item = it.next();
			
			while(item.first().startsWith("I-") && currentEnt.equals(item.first().substring(2))) {
				end = item.third();
				item = it.next();
			}

			Map<String, Object> ent = new HashMap<String, Object>();
			
			Triple<String, Integer, Integer> before = new Triple<String, Integer, Integer>(currentEnt, start, end);
			Triple<String, Integer, Integer> after = PostProcessor.correct(before, text);
			
			ent.put("entity", text.substring(after.second, after.third));
			ent.put("label", after.first);
			ent.put("start", after.second);
			ent.put("end", after.third);
			ents.add(ent);
		}

		res.put("entities", ents);
		JSONObject json = new JSONObject(res);
		return json;
	}
	
	
	public static void writeAnswerInFileConLL(List<List<CoreLabel>> answer, String outFileName) throws FileNotFoundException {
		
		PrintStream outfile = new PrintStream(outFileName);
		for(List<CoreLabel> sentence: answer) {
			for (CoreLabel word : sentence) {
				outfile.println(word.word() + '\t' + word.get(CoreAnnotations.AnswerAnnotation.class) + '\t' + word.beginPosition() + '\t' + word.endPosition());
			}
			outfile.println();
		}
		outfile.close();

	}
	
	public static void writeAnswerInFileConLL(List<Triple<String, Integer, Integer>> answer, String text, PrintStream outfile) {
		for(Triple<String, Integer, Integer> triple : answer) {
			System.out.println(text);
			outfile.println(text.substring(triple.second(), triple.third()) + "\t" + triple.first());
		}
	}
	
	public static Map<String, Object> formatAnswer(List<Triple<String, Integer, Integer>> answer, String text) {

		Map<String, Object> res =  new HashMap<String, Object>();
		res.put("text", text);

		List<Map<String, Object>> ents = new LinkedList<Map<String, Object>>();
		
		//End of list marker
		answer.add(new Triple<String, Integer, Integer>("", -1, -1));
		
		Iterator<Triple<String, Integer, Integer>> it = answer.iterator();
		
		Triple<String, Integer, Integer> item = it.next();
		String currentEnt = "";
		
		while(item.second() != -1) {
			//System.out.println(item + ": " + text.substring(item.second(), item.third()));
			String label = item.first();
			int start = item.second();
			int end = item.third();
			
			if(label.charAt(1) == '-') {
				currentEnt = label.substring(2);
			}
			else {
				currentEnt = label;
				item = it.next();
			}
			
			if(label.startsWith("B-"))
				item = it.next();
			
			while(item.first().startsWith("I-") && currentEnt.equals(item.first().substring(2))) {
				end = item.third();
				item = it.next();
			}

			Map<String, Object> ent = new HashMap<String, Object>();
			Triple<String, Integer, Integer> before = new Triple<String, Integer, Integer>(currentEnt, start, end);
			Triple<String, Integer, Integer> after = PostProcessor.correct(before, text);
			
			ent.put("entity", text.substring(after.second, after.third));
			ent.put("label", after.first);
			ent.put("start", after.second);
			ent.put("end", after.third);
			ents.add(ent);
		}

		res.put("entities", ents);
		return res;
	}
	


	public static void allocate(File dir, String outname) {
		//System.out.println(outname);
		File dout = new File(outname);
		dout.mkdir();
		
		for(File f : dir.listFiles()) {
			if(f.isDirectory()) {
				allocate(f, outname + File.separator + f.getName());
			}
			else {
				
			    if(f.getName().toLowerCase().endsWith(".pdf")) {
			    	//System.out.println(f.getAbsolutePath());
			    	String outFileName = outname + File.separator + f.getName().replaceFirst("\\.[pP][dD][fF]", ".json");
			    	taskList.add(new Pair<File, String>(f, outFileName));
					
			    }
			    else if(f.getName().toLowerCase().endsWith(".html")) {
			    	//System.out.println(f.getAbsolutePath());
			    	String outFileName = outname + File.separator + f.getName().replaceFirst("\\.[hH][tT][mM][lL]", ".json");
			    	taskList.add(new Pair<File, String>(f, outFileName));
			    }
			    else if(f.getName().toLowerCase().endsWith(".txt")) {
			    	//System.out.println(f.getAbsolutePath());
			    	String outFileName = outname + File.separator + f.getName().replaceFirst("\\.[tT][xX][tT]", ".json");
			    	taskList.add(new Pair<File, String>(f, outFileName));
			    }
			}
		}
	}
	
	public static void run(String text, PrintStream outfile) {
		List<Triple<String, Integer, Integer>> answer = classifier.classifyToCharacterOffsets(text);
		List<Triple<String, Integer, Integer>> answer2 = regexNER.ner(text);
		answer.addAll(answer2);
		
		try {
			writeAnswerInFile(answer, "default input", text, outfile);
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}
	}
	
	public static JSONObject classify(String text) {
		List<Triple<String, Integer, Integer>> answer = classifier.classifyToCharacterOffsets(text);
		List<Triple<String, Integer, Integer>> answer2 = regexNER.ner(text);
		answer.addAll(answer2);
		return formatJson(answer, "standard input", text);
	}
	
	
	public static void run(File f, String outFileName) {
        String text = null;
        String cleanedText = null;
        
		System.out.println("Processing " + f.getAbsolutePath());
		if(f.getName().toLowerCase().endsWith(".pdf")) {
	    	text = extractFromPDF(f);
		}
		
	    else if(f.getName().toLowerCase().endsWith(".html")) {
	        text = extractFromHTML(f);
	    }
//	    else if(f.getName().toLowerCase().endsWith(".json")) {
//	    	processJson(f);
//	    	return;
//	    }
	    else { //Assumimos que eh arquivo txt
	    	try {
				text = IOUtils.slurpFile(f);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
	    	
	    }
		
		cleanedText = TextCleaner.cleanText(text);
		if(removeNL)
			cleanedText = TextCleaner.removeNL(cleanedText);

		Map<String, Object> res = new HashMap<>();		
		res.put("src_file", f.getAbsolutePath());
		res.put("file", new File(outFileName).getAbsolutePath());
		Date date = new Date();
		Timestamp time = new Timestamp(date.getTime());
		res.put("timestamp", time.toString());

		if(printSegmented) {
			
			List<Map<String, Object>> sents = new LinkedList<>();
			for(String sentence : segmenter.split(cleanedText)) {
				List<Triple<String, Integer, Integer>> answer = classifier.classifyToCharacterOffsets(sentence);
				List<Triple<String, Integer, Integer>> answer2 = regexNER.ner(sentence);
				answer.addAll(answer2);

				if(sentence.trim().length() > 0)
				{
				    Map<String, Object> formated = formatAnswer(answer, sentence);
				    sents.add(formated);
				}
			}
			res.put("sentences", sents);
			if(sents.size() < 1) {
				return;
			}
		}
		
		else {
			
			List<Triple<String, Integer, Integer>> answer = classifier.classifyToCharacterOffsets(cleanedText);
			List<Triple<String, Integer, Integer>> answer2 = regexNER.ner(cleanedText);
			answer.addAll(answer2);
			
			Map<String, Object> formated = formatAnswer(answer, cleanedText);
			
			res.put("text", formated.get("text"));
			res.put("entities", formated.get("entities"));
		}
		
		PrintStream outfile = null;
		try {
			outfile = new PrintStream(outFileName);
		} catch (FileNotFoundException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		JSONObject json = new JSONObject(res);
		outfile.print(json.toString(4));
		outfile.close();
	}


	public static String extractFromHTML(File f) {
		String text = null;
		FileInputStream inputstream = null;
		HtmlParser parser = new HtmlParser();
		//AutoDetectParser parser = new AutoDetectParser();
		BodyContentHandler handler = new BodyContentHandler();
		Metadata metadata = new Metadata();
		ParseContext parseContext = new ParseContext();

		
		try {
			inputstream = new FileInputStream(f);
		} catch (FileNotFoundException e) {
			System.err.println("Erro ao processar " + f.getAbsolutePath());
			e.printStackTrace();
		}

		//Html parser 
		try {
			parser.parse(inputstream, handler, metadata, parseContext);
		} catch (IOException e) {
			System.err.println("Erro ao processar " + f.getAbsolutePath());
			e.printStackTrace();
		} catch (SAXException e) {
			System.err.println("Erro ao processar " + f.getAbsolutePath());
			e.printStackTrace();
		} catch (TikaException e) {
			System.err.println("Erro ao processar " + f.getAbsolutePath());
			e.printStackTrace();
		}
		try {
			inputstream.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		text = handler.toString();
		return text;
	}

	public static String extractFromPDF(File f) {
		String text = null;
		PDFTextStripper pdftext = null;
		try {
			pdftext = new PDFTextStripper();
		} catch (IOException e) {
			System.err.println("Erro ao processar " + f.getAbsolutePath());
			e.printStackTrace();
		}
		PDDocument doc = null;
		try {
			doc = PDDocument.load(f);
		} catch (IOException e) {
			System.err.println("Erro ao processar " + f.getAbsolutePath());
			e.printStackTrace();
		}

		try {
			text = pdftext.getText(doc);
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}

		try {
			doc.close();
		} catch (IOException e) {
			System.err.println("Erro ao processar " + f.getAbsolutePath());
			e.printStackTrace();
		}
		return text;
	}
}

