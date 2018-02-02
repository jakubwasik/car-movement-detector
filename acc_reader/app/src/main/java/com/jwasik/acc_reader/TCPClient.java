package com.jwasik.acc_reader;

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

public class TCPClient implements Runnable{

    private String serverIP;
    public int serverPort;
    BufferedReader in;
    BufferedWriter out;
    private Socket socket;
    public boolean mRun;

    public TCPClient(String serverIP, int serverPort) {
        this.serverIP = serverIP;
        this.serverPort = serverPort;
    }
    public void stopClient(){
        mRun = false;
    }
    public boolean connect(){
        try{
            InetAddress serverAddr = InetAddress.getByName(serverIP);
            this.socket = new Socket(serverIP, serverPort);
            out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            return true;
        } catch (Exception ex){
            ex.printStackTrace();
            return false;
        }
    }
    public void sendMessage(String message){
        if (out != null) {
            try{
                out.write(message);
                out.flush();
                Log.e("from server", Thread.currentThread().getName());
            }catch(Exception ex){
                ex.printStackTrace();
            }
        }
    }
    public void run(){
        this.connect();
        mRun = true;
        sendMessage("tutaj klient");
        try{
            while (mRun) {
                String serverMessage = in.readLine();

                if (serverMessage != null) {
                    //call the method messageReceived from MyActivity class
                    Log.e("from server - thread:", Thread.currentThread().getName());
                    Log.e("from server", serverMessage);
                }
                serverMessage = null;
            }
            socket.close();
        }catch (Exception ex){
            ex.printStackTrace();
        }
    }

}
