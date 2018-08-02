package com.jwasik.acc_reader;

import android.Manifest;
import android.app.Activity;
import android.content.ContentValues;
import android.content.Context;
import android.content.pm.PackageManager;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.AsyncTask;
import android.os.Environment;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Message;
import android.provider.ContactsContract;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.format.DateFormat;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.GridView;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.sql.Time;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;


public class MainActivity extends AppCompatActivity {
    public TCPClient client;
    ProgressBar pb;
    DataAcquisition configurator;
    private Switch saveToFile;
    private Button sendToServer;
    private Button button;
    private String MODE = "CONTINIOUS DATA";
    private final int READING_PERMISSIONS = 1;
    private final int WRITING_PERMISSIONS = 2;
    private Handler mainHandler;
    private TextView latitude; // latitude
    private TextView longitude; // longitude
    private TextView speed; // longitude
    private GPSManager gps;
    private updateGUI updateGUIRunnable = new updateGUI();
    private static final boolean VERBOSE = true;
    private static final String TAG = "SampleActivity";
    private Button updateGps;
    private final String[] TAGS = {"skret w lewo",
            "skret w prawo",
            "zmiana pasa na lewy", "zmiana pasa na prawy",
            "hamowanie", "zatrzymanie na swiatlach",
            "wyprzedzanie", "przyspieszanie na swiatlach"};

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        this.init();
        GridView gv = findViewById(R.id.gv);

        LazyAdapter adapter = new LazyAdapter(this, TAGS);
        gv.setAdapter(adapter);
        this.requestPermissions();
        Log.e("active threads", String.valueOf(Thread.activeCount()));

        saveToFile.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    if (!configurator.configure())
                        Toast.makeText(getApplicationContext(), "Unable to start thread(no r/w permission)", Toast.LENGTH_LONG);
                    gps.configure();
                    if(MODE != "CONTINIOUS DATA"){
                        configure_event_file();
                    }
                    mainHandler.post(updateGUIRunnable);
                    Set<Thread> threadSet = Thread.getAllStackTraces().keySet();
                    Log.e("active threads", threadSet.toString());
                } else {
                    configurator.cleanThread();
                    gps.cleanThread();
                    if(MODE != "CONTINIOUS DATA"){
                        closeFile();
                    }
                    mainHandler.removeCallbacks(updateGUIRunnable);
                    Set<Thread> threadSet = Thread.getAllStackTraces().keySet();
                    Log.e("active threads", threadSet.toString());
                }
            }
        });
        gv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View v,
                                    int position, long id) {
                if(MODE != "CONTINIOUS DATA"){
                    Toast.makeText(MainActivity.this, "" + position,
                            Toast.LENGTH_SHORT).show();
                    Date currentTime = Calendar.getInstance().getTime();
                    String date = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss:SSS").format(currentTime);
                    String toWrite = date + ";" + TAGS[position] + "\r\n";
                    try {
                        stream.write(toWrite.getBytes());
                    } catch (Exception ex) {
                        Log.e("TE3ST", ex.getMessage().toString());
                    }
                }
            }
        });
    }

    public DateFormat df = new DateFormat();
    private File fobj = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath(), "testy");
    public File newfile;
    FileOutputStream stream;

    private void closeFile() {
        try {
            stream.flush();
            stream.close();
        } catch (Exception ex) {
            Log.e("TE3ST", ex.getMessage().toString());
        }
    }

    private void configure_event_file() {
        String date = df.format("yyyy-MM-dd-HH-mm-ss", new java.util.Date()).toString();

        String filename = "events_" + date + ".csv";
        fobj.mkdirs();
        newfile = new File(fobj, filename);
        try {
            stream = new FileOutputStream(newfile);
        } catch (Exception ex) {
            Log.e("tag", ex.getMessage());
        }
    }

    private void init() {
        saveToFile = findViewById(R.id.saveToFile);
        latitude = findViewById(R.id.latitude);
        longitude = findViewById(R.id.longitude);
        speed = findViewById(R.id.speed);
        configurator = new DataAcquisition(MainActivity.this, mainHandler, "CONTINIOUS_DATA");
        gps = new GPSManager(this, "CONTINIOUS_DATA");
        gps.requestPermissions();
        mainHandler = new Handler();
        client = new TCPClient("13.58.76.62", 8888);
        client.connect(TCPClient.TcpClientMode.FILE_MODE);
    }

    @Override
    public void onRestoreInstanceState(Bundle savedInstanceState) {
        //toRead.setText(savedInstanceState.getString(GAME_STATE_KEY));
        if (VERBOSE) Log.e(TAG, "++ onRestoreInstanceState ++");
    }

    @Override
    public void onSaveInstanceState(Bundle outState) {
        //outState.putString(GAME_STATE_KEY, toRead.getText().toString());
        //outState.putString("GAME", "HEJA");
        // call superclass to save any view hierarchy
        super.onSaveInstanceState(outState);
        if (VERBOSE) Log.e(TAG, "++ onSaveInstanceState ++");
    }

    @Override
    public void onStart() {
        super.onStart();
        if (VERBOSE) Log.e(TAG, "++ ON START ++");
        //configurator.onStart();
    }

    @Override
    public void onResume() {
        super.onResume();
        if (VERBOSE) Log.e(TAG, "+ ON RESUME +");
    }

    @Override
    public void onPause() {
        super.onPause();
        if (VERBOSE) Log.e(TAG, "- ON PAUSE -");
    }

    @Override
    public void onStop() {
        super.onStop();
        if (VERBOSE) Log.e(TAG, "-- ON STOP --");
        //configurator.onStop();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (VERBOSE) Log.e(TAG, "- ON DESTROY -");
    }

    @Override
    public void onRequestPermissionsResult(int requestCode,
                                           String permissions[], int[] grantResults) {
        switch (requestCode) {
            case READING_PERMISSIONS:
            case WRITING_PERMISSIONS: {
                // If request is cancelled, the result arrays are empty.
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {

                    // permission was granted, yay! Do the
                    // contacts-related task you need to do.
                    Log.e("Permissions_read", "permission was granted, yay! ");

                } else {
                    // permission denied, boo! Disable the
                    // functionality that depends on this permission.
                }
                return;
            }
        }
    }

    private void requestPermissions() {
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},
                    READING_PERMISSIONS);
        } else {
            // Permission has already been granted
            Log.e("Permissions", "Reading permission has already been granted");
        }
        // the same for writing
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                    WRITING_PERMISSIONS);
        } else {
            // Permission has already been granted
            Log.e("Permissions", "Writing permissions has already been granted");
        }
    }

    public boolean isExternalStorageWritable() {
        String state = Environment.getExternalStorageState();
        if (Environment.MEDIA_MOUNTED.equals(state)) {
            return true;
        }
        return false;
    }

    /* Checks if external storage is available to at least read */
    public boolean isExternalStorageReadable() {
        String state = Environment.getExternalStorageState();
        if (Environment.MEDIA_MOUNTED.equals(state) ||
                Environment.MEDIA_MOUNTED_READ_ONLY.equals(state)) {
            return true;
        }
        return false;
    }

    class updateGUI implements Runnable {
        @Override
        public void run() {
            try {
                latitude.setText(String.valueOf(gps.latitude));
                longitude.setText(String.valueOf(gps.longitude));
                speed.setText(String.valueOf(gps.speed*3.6));
                if(gps.latitude!= 0 && gps.longitude!=0 ){
                    String toWrite =
                            String.valueOf(configurator.x)
                                    + ";" + String.valueOf(configurator.y)
                                    + ";" + String.valueOf(configurator.z)
                                    + ";" + String.valueOf(gps.latitude)
                                    + ";" + String.valueOf(gps.longitude)
                                    + ";" + String.valueOf(gps.speed)
                                    + "\r\n";
                    client.sendMessage(toWrite);
                }
            } catch (Exception e) {
                // TODO: handle exception
            } finally {
                //also call the same runnable to call it at regular interval
                mainHandler.postDelayed(this, 20);
            }
        }
    }
}
