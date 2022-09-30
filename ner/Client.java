
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Properties;

import org.json.JSONObject;

import preprocessing.TextCleaner;


public class Client {
	
	public static void main(String[] args) throws UnknownHostException, IOException {
		
//		if (args.length < 2) {
//			System.err.println("uso: java -jar mp-ufmg-ner.jar <arquivo de entrada> <arquivo de saida>");
//			System.exit(1);
//		}
		
	    JSONObject json = new JSONObject();

		if (args.length == 2) {
		    json.put("input", args[0]);
		    json.put("output", args[1]);
		}
		else if(args.length == 1) {
			json.put("text", TextCleaner.cleanText(args[0]));
		}
		else { //Read from standard input
			BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
			String text = "";
			String line;
			while((line = reader.readLine()) != null){
				text += (line + "\n");
			}
			json.put("text", TextCleaner.cleanText(text));
		}
		
		Properties prop = new Properties();
		prop.load(new InputStreamReader(new FileInputStream("service_config.txt")));

		int port = Integer.parseInt(prop.getProperty("port"));
		InetAddress host = InetAddress.getByName(prop.getProperty("host"));
		
		//InetAddress host = InetAddress.getLocalHost();
		Socket clientSocket = new Socket(host.getHostName(), port);
		
	    PrintWriter toServer = new PrintWriter(clientSocket.getOutputStream(), true);
	    BufferedReader fromServer = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
	    
	    String request = json.toString(0);
        
	    if (args.length > 1)
	        System.out.println("Request: " + request);
	    toServer.println(request);
	    String answer;
	    while( (answer = fromServer.readLine()) != null) {
	    	System.out.println(answer);
	    }
        
	    fromServer.close();
	    toServer.close();
	    clientSocket.close();
	    
	    /*String answer = "";
	    while((answer = serverAnswer.readLine()) != null) {
	    	System.out.println(answer);
	    }
	    
	    BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
	    
	    
	    
	    while(true) {
	    	String line = in.readLine();
	    	out.print(line);
	    	if(line.trim().equals("quit"))
	    	{
	    		clientSocket.close();
	    		break;
	    	}
	    }*/
	}

}
