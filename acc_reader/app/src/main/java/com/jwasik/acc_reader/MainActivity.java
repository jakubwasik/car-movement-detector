package com.jwasik.acc_reader;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.AsyncTask;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Message;
import android.provider.ContactsContract;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

import java.sql.Time;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;


public class MainActivity extends AppCompatActivity {
    private Handler mainHandler = new Handler() {
        @Override
        public void handleMessage(Message message) {
            bufferMainThread = (ArrayList<ArrayList<SensorData>>) message.obj;
            new DatabaseUploader(bufferMainThread.get(0), uploader).execute();
        }
    };
    private DataBaseManager uploader;
    public TCPClient client;

    private class DatabaseUploader extends AsyncTask<Void, Void, Void> {
        private ArrayList<SensorData> data;
        private DataBaseManager uploader;

        DatabaseUploader(ArrayList<SensorData> data, DataBaseManager uploader) {
            this.data = data;
            this.uploader = uploader;
        }

        protected void onPreExecute() {
            pb.setVisibility(ProgressBar.VISIBLE);
        }

        protected Void doInBackground(Void... params) {
            int tableNr = uploader.getTableNumber();
            uploader.insertIntoResultsTable("SUCCESS");
            uploader.fillDataTable(tableNr + 1, this.data);
            return null;
        }

        protected void onPostExecute(Void result) {
            pb.setVisibility(ProgressBar.INVISIBLE);
        }
    }

    SensorManager manager;
    TextView ax1, ax2, ax3;
    ProgressBar pb;
    ArrayList<ArrayList<SensorData>> bufferMainThread = new ArrayList<ArrayList<SensorData>>(50);
    DataAcquisition configurator;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        ax1 = findViewById(R.id.ax1);
        Button button = findViewById(R.id.button);
        uploader = new DataBaseManager(this);
        pb = findViewById(R.id.progressBar);
        client = new TCPClient("192.168.1.5", 8888);
        Button sendToServer = findViewById(R.id.sendToServer);
        Log.e("aaaaaaaaaaaaaaaaaaa", String.valueOf(Thread.activeCount()));
        sendToServer.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                client.connect(TCPClient.TcpClientMode.FILE_MODE);
                client.sendMessage("Halo tu klient!");
                client.sendMessage("Halo tu klient po raz drugi!");

                client.disconnect();
                Log.e("aaaaaaaaaaaaaaaaaaa", client.connectionHT.getState().toString());
                Log.e("aaaaaaaaaaaaaaaaaaa", String.valueOf(Thread.activeCount()));
            }
        });
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                configurator.getHandler().sendEmptyMessage(0);
                Log.e("aaaaaaaaaaaaaaaaaaa", client.connectionHT.getState().toString());
                Log.e("aaaaaaaaaaaaaaaaaaa", client.disconnectionHT.getState().toString());
                Log.e("aaaaaaaaaaaaaaaaaaa", client.sendHT.getState().toString());
                // for(String elem: runnable.buffer)
                //   Log.e("data", elem);
            }
        });
        ax2 = findViewById(R.id.ax2);
        ax3 = findViewById(R.id.ax3);
        configurator = new DataAcquisition(this, mainHandler);
        configurator.configure();

        //uploader.readTable();
    }

    protected void onResume() {
        super.onResume();
        configurator.onResume();
    }

    protected void onPause() {
        super.onPause();
        configurator.onPause();
    }
}
