package application;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.Charset;

import javafx.application.Platform;
import javafx.scene.control.Label;

public class Listenbackinformation extends Thread {

	private Label systemout;
	private Data data=new Data();
	private static String str;
	
	@SuppressWarnings("static-access")
	public void mystart(Label sys,Data data,String str1)
	{
		this.data=data;
		this.str=str1;
		this.systemout=sys;
	}
	
	public void run() {
		try {
			System.out.println("1");
			Process ps =Runtime.getRuntime().exec(Data.cmdorder,null,data.getfile(str));
			System.out.println("2");
			BufferedReader br = new BufferedReader(new InputStreamReader(ps.getInputStream(), Charset.forName("GBK")));
			String dialog="";
			String line=null;
			//line=br.readLine();
			while((line = br.readLine()) != null)
			{
				Data.dialog=dialog+"\n"+line;
				System.out.println("3");
				Platform.runLater(new Runnable() {
                    @Override
                    public void run() {
                    	systemout.setText(Data.dialog);
                        //更新JavaFX的主线程的代码放在此处
                    }
                });
				//systemout.setText(line);
			}
			//Data.flag=1;
			
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
	}

}
