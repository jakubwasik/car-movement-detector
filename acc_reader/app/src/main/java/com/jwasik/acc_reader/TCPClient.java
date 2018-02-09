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
    private TcpClientState state = TcpClientState.DISCONNECTED;
    public HandlerThread connectionHT;
    public HandlerThread disconnectionHT;
    public HandlerThread sendHT;
    public HandlerThread receiveHT;
    private Handler connectionHandler;
    private Handler disconnectionHandler;
    private Handler sendHandler;
    private Handler receiveHandler;
    private boolean readyToDisconnect = true;

    public enum TcpClientState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        CONNECTION_STARTED,
        FAILED
    }
    public enum TcpClientMode {
        FILE_MODE,
        DATA_MODE
    }
    public TCPClient(String serverIP, int serverPort) {
        this.serverIP = serverIP;
        this.serverPort = serverPort;
    }

    public void connect(TcpClientMode mode)
    {
        readyToDisconnect = false;
        connectionHT = new HandlerThread("Connection with: " + serverIP);
        connectionHT.start();
        connectionHandler = new Handler(connectionHT.getLooper());
        state = TcpClientState.CONNECTING;
        connectionHandler.post(new Connect(mode));
        connectionHT.quitSafely();
    }
    public void sendMessage(String msg)
    {
        readyToDisconnect = false;
        sendHT = new HandlerThread("Send msg to: " + serverIP);
        sendHT.start();
        sendHandler = new Handler(sendHT.getLooper());
        sendHandler.post(new sendMessage(msg));
        sendHT.quitSafely();
    }
    public void disconnect()
    {
        disconnectionHT = new HandlerThread("Disconnection thread");
        disconnectionHT.start();
        disconnectionHandler = new Handler(disconnectionHT.getLooper());
        disconnectionHandler.post(new Disconnect());
        disconnectionHT.quitSafely();
    }
    private class Disconnect implements Runnable{
        @Override
        public void run(){
            while(!readyToDisconnect);
            state = TcpClientState.DISCONNECTED;
        }
    }
    private class Connect implements Runnable{
        private TcpClientMode mode;
        Connect(TcpClientMode mode){
            this.mode = mode;
        }
        @Override
        public void run(){
            try{
                if(state != TcpClientState.CONNECTED) {
                    Log.e("Connected runnable", Thread.currentThread().getName());
                    InetAddress serverAddr = InetAddress.getByName(serverIP);
                    socket = new Socket(serverIP, serverPort);
                    out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                    in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    Log.e("pierwsze connected", Thread.currentThread().getName());
                    state = TcpClientState.CONNECTED;
                    String modeToSend;
                    if(this.mode == TcpClientMode.FILE_MODE)
                        modeToSend = "Send File";
                    else
                        modeToSend = "Send Continuous Data";
                    out.write(modeToSend);
                    out.flush();
                }
                else{
                    Log.e("Connection Exists!", Thread.currentThread().getName());
                }
                while (state == TcpClientState.CONNECTED) {
                    //String serverMessage = in.readLine();
                    //if (serverMessage != null) {
                        //call the method messageReceived from MyActivity class
                     //   Log.e("DEBUGGING THREAD", Thread.currentThread().getName());
                     //   Log.e("Received from server", serverMessage);
                    //}
                    //readyToDisconnect = true;
                  //  serverMessage = null;
                }
                Log.e("DISCONNECTING", Thread.currentThread().getName());
                in.close();
                out.flush();
                out.close();
                socket.close();
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
            while(state != TcpClientState.CONNECTED);
            if (true) {
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
                    Log.e("from server", Thread.currentThread().getName());

                }catch(Exception ex){
                    ex.printStackTrace();
                    state = TcpClientState.FAILED;
                }
            }
            readyToDisconnect = true;
        }
    }
   /* private class ReceiveFromServer implements Runnable{
        @Override
        public void run(){
            try{

            }catch (Exception ex){
                ex.printStackTrace();
                state = TcpClientState.FAILED;
            }
        }
    }*/
}
