package com.jwasik.acc_reader;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.os.Message;
import android.text.format.DateFormat;
import android.util.Log;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

class Buffer{
    public ArrayList<String> data;
    public int windowSize;
    public int slidingWindow;
    Buffer(int size, int windowSize, int slidingWindow){
         data = new ArrayList<String>(size);
         this.windowSize = windowSize;
         this.slidingWindow = slidingWindow;
    }
    public void addElem(String elem){
        if(data.size()<this.windowSize)
            data.add(elem);
        else{
            data.remove(0);
            data.add(elem);
        }
    }
    public String getDataToSend(){
        String toSend = new String();
        for(int i=0; i<data.size(); i++)
            toSend += data.get(i);
        for(int i=0; i<slidingWindow; i++)
            data.remove(0);
        return toSend;
    }
    public boolean readyToSend(){
        return data.size()==this.windowSize ? true: false;
    }
}

class DataAcquisition{

    private MainActivity mContext;
    private GPSManager gps;
    private SensorManager mSensorManager = null;
    private SensorEventListener mListener;
    private HandlerThread mHandlerThread;
    public Handler mainHandler;
    public Buffer data;
    public Handler fileSizeHandler;
    public DateFormat df;
    long i = 0;
    public float x,y,z;
    public String MODE;
    public File newfile;
    private File fobj;
    public TCPClient client;
    private boolean configured = false;
    FileOutputStream stream;
    private Handler threadHandler ;
    DataAcquisition(MainActivity context, Handler mainHandler, String MODE, TCPClient client, GPSManager gps) {
        this.client = client;
        this.gps = gps;
        mContext = context;
        this.MODE=MODE;
        data = new Buffer(260, 250,100);
        this.mainHandler = mainHandler;
        mSensorManager = (SensorManager) mContext.getSystemService(Context.SENSOR_SERVICE);
        if(this.MODE != "CONTINIOUS_DATA"){
            fobj = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath(), "testy");
            df = new DateFormat();
        }
    }

    public boolean configure() {
        if (!mContext.isExternalStorageWritable() || !mContext.isExternalStorageReadable()) {
            return false;
        }
        if(this.MODE != "CONTINIOUS_DATA"){
            String date = df.format("yyyy-MM-dd-HH-mm-ss", new java.util.Date()).toString();
            Log.e("FileName", date);
            String filename = "raw_data_" + date + ".csv";
            fobj.mkdirs();
            newfile = new File(fobj, filename);
            try{
                stream = new FileOutputStream(newfile);
            }catch(Exception ex){
                Log.e("tag",  ex.getMessage() );
            }
        }
        mHandlerThread = new HandlerThread("AccelerometerLogListener");
        mHandlerThread.start();
        threadHandler = new Handler(mHandlerThread.getLooper());
        Log.e("tesst", mSensorManager.getSensorList(Sensor.TYPE_GYROSCOPE_UNCALIBRATED).toString());
        mListener = new SensorEventListener() {
            @Override
            public void onSensorChanged(SensorEvent sensorEvent) {
                if(MODE != "CONTINIOUS_DATA"){
                    if (sensorEvent.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
                        try{
                            Date currentTime = Calendar.getInstance().getTime();
                            String date = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss:SSS").format(currentTime);
                            String toWrite =  date
                                    + ";" + String.valueOf(sensorEvent.values[0])
                                    + ";" + String.valueOf(sensorEvent.values[1])
                                    + ";" + String.valueOf(sensorEvent.values[2])
                                    + "\r\n";
                            stream.write(toWrite.getBytes());
                        }catch(Exception ex){
                            Log.e("TEST", ex.getMessage().toString());
                        }
                    }
                }else{
                    if (sensorEvent.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
                        if(gps.latitude!= 0 && gps.longitude!=0 ){
                            Date currentTime = Calendar.getInstance().getTime();
                            String date = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss:SSS").format(currentTime);
                            String toWrite =  date
                                    + ";" + String.valueOf(sensorEvent.values[0])
                                    + ";" + String.valueOf(sensorEvent.values[1])
                                    + ";" + String.valueOf(sensorEvent.values[2])
                                    + ";" + String.valueOf(gps.latitude)
                                    + ";" + String.valueOf(gps.longitude)
                                    + ";" + String.valueOf(gps.speed)
                                    + "\r\n";
                            data.addElem(toWrite);
                        }
                        if(data.readyToSend() == true){
                            client.sendMessage(data.getDataToSend());
                        }
                        i++;
                    }
                }
            }
            @Override
            public void onAccuracyChanged(Sensor sensor, int accuracy) {

            }
        };

        mSensorManager.registerListener(mListener,
                                        mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),
                                        SensorManager.SENSOR_DELAY_GAME,
                                        threadHandler);
        Log.e("test",String.valueOf(mSensorManager.registerListener(mListener,
                                        mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE),
                                        SensorManager.SENSOR_DELAY_NORMAL,
                                        threadHandler)));
        configured = true;
        return true;
    }
    public void onStart() {
        if(configured){
            mSensorManager.registerListener(mListener,
                    mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),
                    SensorManager.SENSOR_DELAY_NORMAL,
                    threadHandler);
        }
    }

    public void onStop() {
        // never forget to unregister
        mSensorManager.unregisterListener(mListener);
    }


    public void cleanThread(){

        //Unregister the listener
        if(this.MODE != "CONTINIOUS DATA"){
            if(configured) {
                try{
                    stream.close();
                }catch (Exception ex){
                    //todo
                }
        }
            mSensorManager.unregisterListener(mListener);
        }

        if(mHandlerThread.isAlive())
            mHandlerThread.quitSafely();
        configured = false;
    }
    public Handler getHandler() {
        return threadHandler;
    }
}

