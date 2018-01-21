package com.jwasik.acc_reader;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.sql.Time;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private Handler mainHandler = new Handler(){
        @Override
        public void handleMessage(Message message){
            bufferMainThread = (ArrayList<ArrayList<SensorData>>)message.obj;
            for(SensorData elem: bufferMainThread.get(0))
                Log.e("data", String.valueOf(elem.getData()[2]));
        }
    };
    SensorManager manager;
    TextView ax1,ax2,ax3;
    ArrayList<ArrayList<SensorData>> bufferMainThread = new ArrayList<>(50);
    DataAcquisition runnable;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        ax1 = findViewById(R.id.ax1);
        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                runnable.getHandler().sendEmptyMessage(0);
               // for(String elem: runnable.buffer)
                 //   Log.e("data", elem);
            }
        });
        ax2 = findViewById(R.id.ax2);
        ax3 = findViewById(R.id.ax3);
        runnable = new DataAcquisition(this, mainHandler);
        Thread thread = new Thread(runnable);
        thread.start();
    }
    protected void onResume() {
        super.onResume();
        runnable.onResume();
    }

    protected void onPause() {
        super.onPause();
        runnable.onPause();
    }
}