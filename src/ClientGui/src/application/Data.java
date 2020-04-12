package application;

import java.io.File;

public class Data {
	public static String ip;
	public static String port;
	public static String cmdorder;
	public static String str1;
	public static String filestring;
	public static File directory;
	public static int flag;
	public static String dialog;
	@SuppressWarnings("static-access")
	public Data()
	{
		flag=0;
		this.str1="python client.py ";
	}
	
	public void clear()
	{
		flag=0;
		ip="";
		port="";
		cmdorder="";
		filestring="";
		directory=null;
		dialog="";
	}
	
	public File getfile(String str)
	{
		directory=new File(str);
		return directory;
	}
}
