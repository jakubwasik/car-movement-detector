package com.jwasik.acc_reader;

import android.os.Handler;
import android.os.HandlerThread;
import android.util.Log;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.io.*;

/**
 * Created by kuba on 2018-02-01.
 */

public class TCPClient{

    private String serverIP;
    private int serverPort;
    private BufferedReader in;
    private BufferedWriter out;
    private Socket socket;
    public boolean mRun;
    public TcpClientState state;
    public HandlerThread connectionHT;
    public HandlerThread sendHT;
    public HandlerThread receiveHT;
    private Handler connectionHandler;
    private Handler receiveHandler;
    private TcpClientMode mode;

    public enum TcpClientState {
        DISCONNECTED,
        CONNECTED,
        FAILED,
        DISCONNECTING
    }
    public enum TcpClientMode {
        FILE_MODE,
        DATA_MODE
    }
    public TCPClient(String serverIP, int serverPort) {
        this.serverIP = serverIP;
        this.serverPort = serverPort;
        this.state = TcpClientState.DISCONNECTED;
    }

    public void connect(TcpClientMode mode)
    {
         if(state == TcpClientState.DISCONNECTED){

            connectionHT = new HandlerThread("Connection with: " + serverIP);
            connectionHT.start();
            connectionHandler = new Handler(connectionHT.getLooper());
            connectionHandler.post(new Connect(mode));
            this.mode = mode;
            if(mode == TcpClientMode.DATA_MODE){
                receiveFromServer();
            }
             state = TcpClientState.CONNECTED;
        }
        else{
            Log.e("[TCPClient.connect]","Connection already exists!");
        }
    }

    public void receiveFromServer(){
        receiveHT = new HandlerThread("Thread: receive from: " + serverIP);
        receiveHT.start();
        receiveHandler = new Handler(receiveHT.getLooper());
        receiveHandler.post(new Runnable() {
            @Override
            public void run() {
                try{
                    while(state == TcpClientState.CONNECTED){
                        in.read();
                    }
                }catch (Exception ex){
                    ex.printStackTrace();
                    state = TcpClientState.FAILED;
                }
            }
        });
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
            if(this.mode == TcpClientMode.DATA_MODE){
                receiveHT.quitSafely();
            }
            connectionHT.quitSafely();
        }
        else
            Log.e("[TCPClient.disconnect]", "Connection already disconnected!");
    }

    private class Connect implements Runnable{
        private TcpClientMode mode;
        Connect(TcpClientMode mode){
            this.mode = mode;
        }
        @Override
        public void run(){
            try{

                InetAddress serverAddr = InetAddress.getByName(serverIP);
                socket = new Socket(serverIP, serverPort);
                Log.e("DDDDDD", Thread.currentThread().getName());
                out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String modeToSend;
                if(this.mode == TcpClientMode.FILE_MODE)
                    modeToSend = "Send File";
                else
                    modeToSend = "Send Continuous Data";
                out.write(modeToSend);
                out.flush();

            }catch (Exception ex){
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
                    int msgSize = message.length();
                    Log.e("przed wyslaniem", message);
                    out.write("Wysylam CSV: " + String.valueOf(msgSize));
                    out.flush();
                    char[] buffer = new char[1024];
                    int charsReaded = in.read(buffer, 0,  1024);
                    String bufferStr = new String(buffer, 0, charsReaded);
                    Log.e("Ile odczytalo znakow", String.valueOf(bufferStr));
                    if(Integer.parseInt(bufferStr) == msgSize){
                        out.write(message, 0 ,msgSize);
                        out.flush();
                    }
                    else{
                        Log.e("DEBUG", "Server odesłał zła ilość danych.");
                    }
                    Log.e("from server", Thread.currentThread().getName());
                }catch(Exception ex){
                    ex.printStackTrace();
                    state = TcpClientState.FAILED;
                }
        }
    }
}
