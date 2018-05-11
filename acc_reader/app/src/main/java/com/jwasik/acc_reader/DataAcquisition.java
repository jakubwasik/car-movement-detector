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


class DataAcquisition{

    private MainActivity mContext;
    private SensorManager mSensorManager = null;
    private SensorEventListener mListener;
    private HandlerThread mHandlerThread;
    public Handler mainHandler;
    private boolean createNewFile = false;
    public Handler fileSizeHandler;
    public DateFormat df;
    long i = 0;
    public File newfile;
    private File fobj;
    private boolean configured = false;
    FileOutputStream stream;
    Runnable monitorTask = new fileSizeMonitor();
    HandlerThread fileSizeHandlerThread;
    private Handler threadHandler ;
    DataAcquisition(MainActivity context, Handler mainHandler) {
        mContext = context;
        this.mainHandler = mainHandler;
        mSensorManager = (SensorManager) mContext.getSystemService(Context.SENSOR_SERVICE);
        fobj = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath(), "testy");
        df = new DateFormat();
    }


    public boolean configure() {
        if (!mContext.isExternalStorageWritable() || !mContext.isExternalStorageReadable()) {
            return false;
        }
        String date = df.format("yyyy-MM-dd-HH-mm-ss", new java.util.Date()).toString();
        Log.e("FileName", date);
        String filename = "raw_data_" + date + ".csv";
        mHandlerThread = new HandlerThread("AccelerometerLogListener");
        mHandlerThread.start();
        threadHandler = new Handler(mHandlerThread.getLooper());
        fobj.mkdirs();
        newfile = new File(fobj, filename);
        try{
            stream = new FileOutputStream(newfile);
        }catch(Exception ex){
            Log.e("tag",  ex.getMessage() );
        }
        fileSizeHandlerThread = new HandlerThread("fileSizeHandlerThread");
        fileSizeHandlerThread.start();
        fileSizeHandler = new Handler(fileSizeHandlerThread.getLooper());
        fileSizeHandler.postDelayed(monitorTask, 5000);


        Log.e("tesst", mSensorManager.getSensorList(Sensor.TYPE_GYROSCOPE_UNCALIBRATED).toString());
        mListener = new SensorEventListener() {
            @Override
            public void onSensorChanged(SensorEvent sensorEvent) {
                if (sensorEvent.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
                    try{
                        if ( createNewFile){
                            String date = df.format("yyyy-MM-dd-HH-mm-ss", new java.util.Date()).toString();
                            Log.e("FileName", date);
                            String filename = "raw_data_" + date + ".csv";
                            stream.flush();
                            stream.close();
                            newfile = new File(fobj, filename);
                            stream = new FileOutputStream(newfile);
                            createNewFile= false;
                        }
                        Date currentTime = Calendar.getInstance().getTime();
                        String date = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss:SSS").format(currentTime);
                        String toWrite =  date
                                + ";" + String.valueOf(sensorEvent.values[0])
                                + ";" + String.valueOf(sensorEvent.values[1])
                                + ";" + String.valueOf(sensorEvent.values[2])
                                + "\r\n";
                        stream.write(toWrite.getBytes());
                    }catch(Exception ex){
                        Log.e("TE3ST", ex.getMessage().toString());
                    }

                }/*else if (sensorEvent.sensor.getType() == Sensor.TYPE_GYROSCOPE) {
                    bufferGyro.add(new SensorData(sensorEvent.timestamp,sensorEvent.values.clone()));
                    Log.e("test", String.valueOf(formatted));

                }*/
                i++;
                //if (mIsServiceStarted && mFileStream != null && mLogFile.exists()) {
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
            mSensorManager.registerListener(mListener,
                    mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE),
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
        if(configured) {
            try{
                stream.close();
            }catch (Exception ex){
                //todo
            }
            mSensorManager.unregisterListener(mListener);
        }

        if(mHandlerThread.isAlive())
            mHandlerThread.quitSafely();
        fileSizeHandler.removeCallbacks(monitorTask);
        fileSizeHandlerThread.quit();
        configured = false;
    }
    public Handler getHandler() {
        return threadHandler;
    }

    class fileSizeMonitor implements Runnable{
        @Override
        public void run() {
            try{
                String test = "background";
                if(newfile.length()/1024 > 5000000){
                    createNewFile = true;
                    Log.e("Filesize monitor", test);
                }

            }
            catch (Exception e) {
                // TODO: handle exception
            }
            finally{
                //also call the same runnable to call it at regular interval
                fileSizeHandler.postDelayed(this, 5000);
            }
        }
    }
}

