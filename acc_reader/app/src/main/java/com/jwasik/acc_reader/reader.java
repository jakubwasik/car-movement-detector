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
import android.util.Log;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by Saeid on 22-4-2014.
 */
class SensorData{
    private long timestamp;
    private float[] data;
    SensorData(long timestamp, float [] data){
        this.timestamp = timestamp;
        this.data = data;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }

    public float[] getData() {
        return data;
    }

    public void setData(float[] data) {
        this.data = data;
    }
}
class DataAcquisition implements Runnable {

    private MainActivity mContext;
    private SensorManager mSensorManager = null;
    private File mLogFile = null;
    private FileOutputStream mFileStream = null;
    private SensorEventListener mListener;
    private HandlerThread mHandlerThread;
    public Handler mainHandler;
    public String formatted;
    long i = 0;
    public ArrayList<SensorData> bufferAcc = new ArrayList<SensorData>(50);
    public ArrayList<SensorData> bufferGyro = new ArrayList<SensorData>(50);
    DataAcquisition(MainActivity context, Handler mainHandler) {
        mContext = context;
        this.mainHandler = mainHandler;
    }
    private Handler threadHandler ;
    /**
     * Sets up folder and file to log the file on it
     */

    @Override
    public void run() {
        mSensorManager = (SensorManager) mContext.getSystemService(Context.SENSOR_SERVICE);
        mHandlerThread = new HandlerThread("AccelerometerLogListener");
        mHandlerThread.start();
        threadHandler = new Handler(mHandlerThread.getLooper()){
            @Override
            public void handleMessage(Message message){
                Bundle msgBundle = new Bundle();
                //msgBundle.putString("result", formatted);
                Message msg = new Message();
                ArrayList<ArrayList<SensorData>> toSend = new ArrayList<>(2);
                toSend.add(bufferAcc);
                toSend.add(bufferGyro);
                msg.obj=toSend;
                //sg.setData(msgBundle);
                mainHandler.sendMessage(msg);
            }
        };
        mListener = new SensorEventListener() {
            @Override
            public void onSensorChanged(SensorEvent sensorEvent) {
                if (sensorEvent.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
                    bufferAcc.add(new SensorData(sensorEvent.timestamp,sensorEvent.values.clone()));


                }else if (sensorEvent.sensor.getType() == Sensor.TYPE_GYROSCOPE) {
                    bufferGyro.add(new SensorData(sensorEvent.timestamp,sensorEvent.values));

                }
                formatted = String.valueOf(sensorEvent.timestamp)
                        + "\t" + String.valueOf(Thread.currentThread().getName())
                        + "\t" + String.valueOf(sensorEvent.values[0])
                        + "\t" + String.valueOf(sensorEvent.values[1])
                        + "\t" + String.valueOf(sensorEvent.values[2])
                        + "\r\n";
                i++;
                Log.e("test", String.valueOf(formatted));
                if(bufferAcc.size()>50)
                {
                    bufferAcc.remove(0);
                }
                if(bufferGyro.size()>50)
                {
                    bufferGyro.remove(0);
                }
                //Log.e("test", formatted);
                //if (mIsServiceStarted && mFileStream != null && mLogFile.exists()) {
            }

            @Override
            public void onAccuracyChanged(Sensor sensor, int accuracy) {

            }
        };

        mSensorManager.registerListener(mListener,
                                        mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),
                                        SensorManager.SENSOR_DELAY_NORMAL,
                                        threadHandler);
        mSensorManager.registerListener(mListener,
                                        mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE),
                                        SensorManager.SENSOR_DELAY_NORMAL,
                                        threadHandler);
    }
    public void onResume() {
        if(mSensorManager.)
        mSensorManager.registerListener(mListener,
                mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),
                SensorManager.SENSOR_DELAY_NORMAL,
                threadHandler);
        mSensorManager.registerListener(mListener,
                mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE),
                SensorManager.SENSOR_DELAY_NORMAL,
                threadHandler);
    }

    public void onPause() {

        // never forget to unregister
        mSensorManager.unregisterListener(mListener);
    }


    public void cleanThread(){

        //Unregister the listener
        if(mSensorManager != null) {
            mSensorManager.unregisterListener(mListener);
        }

        if(mHandlerThread.isAlive())
            mHandlerThread.quitSafely();
    }
    public Handler getHandler() {
        return threadHandler;
    }
}