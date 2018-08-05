package com.jwasik.carmovementanalyzer;

import android.os.Handler;
import android.os.HandlerThread;
import android.util.Log;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.io.*;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 * Created by kuba on 2018-02-01.
 */

public class TCPClient{

    private String serverIP;
    public String event_detected;
    private int serverPort;
    private BufferedReader in;
    private BufferedWriter out;
    private Socket socket;
    public TcpClientState state;
    public HandlerThread connectionHT;
    private Handler connectionHandler;
    private boolean useGps;
    private String classfier;

    public enum TcpClientState {
        DISCONNECTED,
        CONNECTED,
        FAILED,
        DISCONNECTING
    }
    public TCPClient(String serverIP, int serverPort, Boolean useGps, String classfier) {
        this.serverIP = serverIP;
        this.serverPort = serverPort;
        this.state = TcpClientState.DISCONNECTED;
        this.useGps = useGps;
        this.classfier = classfier;
    }

    public void connect()
    {
        if(state == TcpClientState.DISCONNECTED){

            connectionHT = new HandlerThread("Connection with: " + serverIP);
            connectionHT.start();
            connectionHandler = new Handler(connectionHT.getLooper());
            connectionHandler.post(new Connect());
            state = TcpClientState.CONNECTED;
        }
        else{
            Log.e("[TCPClient.connect]","Connection already exists!");
        }
    }

    public void sendMessage(String msg)
    {

        if(state == TcpClientState.CONNECTED)

            connectionHandler.post(new sendMessage(msg));
        else
            Log.e("[TCPClient.sendMessage]", "Connection already disconnected!");
    }

    public void disconnect()
    {
        if(state == TcpClientState.CONNECTED || state == TcpClientState.FAILED){
            state = TcpClientState.DISCONNECTING;
            connectionHandler.post(new Runnable(){
                @Override
                public void run(){
                    try {
                        Log.e("DISCONNECTING", Thread.currentThread().getName());
                        in.close();
                        out.flush();
                        out.close();
                        socket.close();
                        state = TcpClientState.DISCONNECTED;
                    } catch (Exception ex) {
                        ex.printStackTrace();
                    }
                }
            });
            connectionHT.quitSafely();
        }
        else
            Log.e("[TCPClient.disconnect]", "Connection already disconnected!");
    }

    private class Connect implements Runnable{
        @Override
        public void run(){
            try{
                InetAddress serverAddr = InetAddress.getByName(serverIP);
                socket = new Socket(serverIP, serverPort);
                Log.e("[TCPClient]", Thread.currentThread().getName());
                out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String modeToSend;
                modeToSend = "Use Classifier: " + classfier + "\n";
                if(useGps)
                    modeToSend+= "GPS: Enabled";
                else
                    modeToSend+= "GPS: Disabled";
                out.write(modeToSend);
                out.flush();
            }catch (Exception ex){
                Log.e("[TCPClient]", ex.getMessage());
                ex.printStackTrace();
                state = TcpClientState.FAILED;
            }
        }
    }
    private class sendMessage implements Runnable{
        private String message;
        sendMessage(String msg){
            this.message = msg;
        }
        @Override
        public void run(){
            try{
                Date currentTime = Calendar.getInstance().getTime();
                String date = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss:SSS").format(currentTime);
                Log.e("START DATE", date);
                int msgSize = message.length();
                out.write("Wysylam CSV: " + String.valueOf(msgSize));
                out.flush();
                char[] buffer = new char[1024];
                int charsReaded = in.read(buffer, 0,  1024);
                String bufferStr = new String(buffer, 0, charsReaded);
                Log.e("Ile odczytalo znakow", String.valueOf(bufferStr));
                if(Integer.parseInt(bufferStr) == msgSize) {
                    out.write(message, 0, msgSize);
                    out.flush();
                }
                else{
                    Log.e("DEBUG", "Server odesłał zła ilość danych.");
                }
                currentTime = Calendar.getInstance().getTime();
                date = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss:SSS").format(currentTime);
                Log.e("STOP DATE", date);
                Log.e("from server", Thread.currentThread().getName());
                buffer = new char[1024];
                charsReaded = in.read(buffer, 0,  1024);
                event_detected = new String(buffer, 0, charsReaded);
                Log.e("EVENT DETECTED:", event_detected);
            }catch(Exception ex){
                ex.printStackTrace();
                state = TcpClientState.FAILED;
            }
        }
    }
}
