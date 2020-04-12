package application;
	
//import java.awt.TextArea;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.Charset;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.stage.Stage;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.stage.DirectoryChooser;
import javafx.stage.FileChooser;

public class Main extends Application {
	@Override
	public void start(Stage primaryStage) {
		try {
			Parent parent = FXMLLoader.load(getClass().getResource("Clientscene.fxml"));
			Scene scene = new Scene(parent,840,490);

			Button choosefile = (Button) parent.lookup("#choosefile");
			Button choosefolder = (Button) parent.lookup("#folder");
			Button transport =(Button) parent.lookup("#transport");
			Button transport_zip =(Button) parent.lookup("#transport_zip");
			Label fileout=(Label) parent.lookup("#fileout");
			Label systemout=(Label) parent.lookup("#systemout");
			TextField field1 =(TextField) parent.lookup("#field1");
			TextField field2 =(TextField) parent.lookup("#field2");
			//TextArea textarea = (TextArea) parent.lookup("#textarea");
			
			
			String str=System.getProperty("user.dir");
			Data data =new Data();
			
			//System.out.println(directory.getAbsolutePath());//获取绝对路径
			//System.out.println(System.getProperty("user.dir"));
			choosefile.setOnAction(e->{
				FileChooser filechoose =new FileChooser();
				//DirectoryChooser directoryChooser=new DirectoryChooser();
				filechoose.setTitle("请选择文件");
				File file =  filechoose.showOpenDialog(new Stage());
				//File file =  directoryChooser.showDialog(new Stage());
				if(file==null) return;
				Data.filestring=file.getAbsolutePath();
				fileout.setText(Data.filestring);
				//System.out.println(file.getAbsolutePath());
			});
			
			choosefolder.setOnAction(e->{

				DirectoryChooser directoryChooser=new DirectoryChooser();
				File file =  directoryChooser.showDialog(new Stage());
				if(file==null) return;
				Data.filestring=file.getAbsolutePath();
				fileout.setText(Data.filestring);
				//System.out.println(file.getAbsolutePath());
			});
			
			transport.setOnAction(e ->{
				Data.directory = new File("");
				Data.ip=field1.getText();
				Data.port=field2.getText();
				Data.cmdorder=Data.str1+Data.filestring+" "+Data.ip+" "+Data.port;
				try {
					Process ps =Runtime.getRuntime().exec(Data.cmdorder,null,data.getfile(str));
					BufferedReader br = new BufferedReader(new InputStreamReader(ps.getInputStream(), Charset.forName("GBK")));
					String dialog=null;
					String line=null;
					//line=br.readLine();
					while((line = br.readLine()) != null)
					{
						dialog=dialog+"\n"+line;
						systemout.setText(line);
					}
					
					/*else
					{
						systemout.setText("传输失败，请重试");
					}*/
				} catch (IOException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				data.clear();
			});
			
			transport_zip.setOnAction(e ->{
				Data.directory = new File("");
				Data.ip=field1.getText();
				Data.port=field2.getText();
				Data.cmdorder=Data.str1+Data.filestring+" "+Data.ip+" "+Data.port+" zip";
				try {
					Runtime.getRuntime().exec(Data.cmdorder,null,data.getfile(str));
				} catch (IOException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				data.clear();
			});
			
			scene.getStylesheets().add(getClass().getResource("application.css").toExternalForm());
			primaryStage.setScene(scene);
			primaryStage.show();
		} catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	public static void main(String[] args) {
		launch(args);
	}
}
