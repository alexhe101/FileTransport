package application;

import java.io.File;

public class Data {
	public static String ip;
	public static String port;
	public static String cmdorder;
	public static String str1;
	public static String filestring;
	public static File directory;
	@SuppressWarnings("static-access")
	public Data()
	{
		this.str1="python client.py ";
	}
	
	public void clear()
	{
		ip="";
		port="";
		cmdorder="";
		filestring="";
		directory=null;
	}
	
	public File getfile(String str)
	{
		directory=new File(str);
		return directory;
	}
}
