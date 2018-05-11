package com.jwasik.acc_reader;

import android.Manifest;
import android.app.Activity;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.text.format.DateFormat;
import android.util.Log;

import java.io.File;
import java.io.FileOutputStream;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 * Created by kuba on 2018-04-16.
 */

public class GPSManager extends Service implements LocationListener {
    private Context mContext;
    private Criteria cr;
    private Location location;
    private LocationManager locationManager;
    private String provider;
    private HandlerThread handlerThread;
    public double latitude; // latitude
    public double longitude; // longitude
    FileOutputStream stream;
    Handler gpsHandler;
    public File newfile;
    private File fobj;
    private boolean createNewFile = false;
    public double speed;
    public DateFormat df;
    // The minimum distance to change Updates in meters
    private static final long MIN_DISTANCE_CHANGE_FOR_UPDATES = 0; // 10 meters

    // The minimum time between updates in milliseconds
    private static final long MIN_TIME_BW_UPDATES = 0; // 1 minute
    GPSManager(Context context){
        this.mContext = context;

    }
    public void configure(){
        this.init();
        gpsHandler.post(new writeToFile());
    }
    public double getLatitude(){
        try{
            Location loc = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            return loc.getLatitude();
        }catch(SecurityException e){
            Log.e("GPS Enabled", e.getMessage());
        }
        return -1;
    }
    public double getLongitude(){

        try{
            Location loc = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            return loc.getLongitude();
        }catch(SecurityException e){
            Log.e("GPS Enabled", e.getMessage());
        }
        return -1;
    }
    public double getSpeed(){
        try{
            Location loc = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            return loc.getSpeed();
        }catch(SecurityException e){
            Log.e("GPS Enabled", e.getMessage());
        }
        return -1;
    }
    public boolean init(){
        //cr = new Criteria();
        //cr.setSpeedAccuracy(Criteria.ACCURACY_HIGH);
        //cr.setSpeedRequired(true);
        handlerThread = new HandlerThread("GPS thread");
        handlerThread.start();
        gpsHandler = new Handler(handlerThread.getLooper());
        locationManager = (LocationManager) mContext.getSystemService(LOCATION_SERVICE);
        fobj = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath(), "testy");
        fobj.mkdirs();
        boolean gps_enabled = locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER);
        if(gps_enabled){
            try{
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,
                        MIN_TIME_BW_UPDATES,
                        MIN_DISTANCE_CHANGE_FOR_UPDATES,
                        this);
            }catch(SecurityException e){
                Log.e("GPS Enabled", e.getMessage());
                gps_enabled = false;
            }
        }
        String date = df.format("yyyy-MM-dd-HH-mm-ss", new java.util.Date()).toString();
        Log.e("FileName", String.valueOf(createNewFile));
        String filename = "gps_data_" + date + ".csv";
        newfile = new File(fobj, filename);
        try{
            stream = new FileOutputStream(newfile);
        }catch(Exception ex){

        }

        return gps_enabled;
    }
    public void writeFile(){}
    public void stopUsingGPS(){
        if(locationManager != null){
            locationManager.removeUpdates(GPSManager.this);
        }
    }
    @Override
    public void onLocationChanged(Location location) {
        Log.e("GPS Enabled1", String.valueOf(latitude));
        latitude = location.getLatitude();
        longitude = location.getLongitude();
        speed = location.getSpeed(); // unit: m/s
    }

    @Override
    public void onProviderDisabled(String provider) {
    }

    @Override
    public void onProviderEnabled(String provider) {
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
    }
    @Override
    public IBinder onBind(Intent arg0) {
        return null;
    }
    void requestPermissions(){
        if (ContextCompat.checkSelfPermission(mContext,
                Manifest.permission.ACCESS_FINE_LOCATION)
                != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions((Activity)mContext,
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION},
                    1);
        } else {
            // Permission has already been granted
            Log.e("Permissions", "ACCESS_FINE_LOCATION permission has already been granted");
        }
        // the same for INTERNET
        if (ContextCompat.checkSelfPermission(mContext,
                Manifest.permission.INTERNET)
                != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions((Activity)mContext,
                    new String[]{Manifest.permission.INTERNET},
                    2);
        } else {
            Log.e("Permissions", "INTERNET permission has already been granted");
        }
    }
    public void cleanThread(){
            try{
                stream.close();
            }catch (Exception ex){
                //todo
            }
        this.stopUsingGPS();

        if(handlerThread.isAlive())
            handlerThread.quitSafely();
    }
    class writeToFile implements Runnable{
        @Override
        public void run() {
            try{
                if ( createNewFile){
                    String date = df.format("yyyy-MM-dd-HH-mm-ss", new java.util.Date()).toString();
                    Log.e("FileName", String.valueOf(createNewFile));
                    String filename = "gps_data_" + date + ".csv";
                    stream.flush();
                    stream.close();
                    newfile = new File(fobj, filename);
                    stream = new FileOutputStream(newfile);
                    createNewFile= false;
                }
                Date currentTime = Calendar.getInstance().getTime();
                String date = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss:SSS").format(currentTime);
                String toWrite =  date
                        + ";" + String.valueOf(getLatitude())
                        + ";" + String.valueOf(getLongitude())
                        + ";" + String.valueOf(getSpeed()*3.6)
                        + "\r\n";

                /*
                String toWrite =  date
                        + ";" + String.valueOf(latitude)
                        + ";" + String.valueOf(longitude)
                        + ";" + String.valueOf(speed*3.6)
                        + "\r\n";
                */
                stream.write(toWrite.getBytes());
            }
            catch (Exception e) {
                // TODO: handle exception
            }
            finally{
                //also call the same runnable to call it at regular interval
                gpsHandler.postDelayed(this, 20);
            }
        }
    }
}
