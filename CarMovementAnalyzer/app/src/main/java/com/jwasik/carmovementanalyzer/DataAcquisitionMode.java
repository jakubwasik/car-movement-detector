package com.jwasik.carmovementanalyzer;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.support.v4.app.ActivityCompat;
import android.support.v4.app.Fragment;
import android.support.v4.content.ContextCompat;
import android.text.format.DateFormat;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.CompoundButton;
import android.widget.GridView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Set;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link DataAcquisitionMode.OnFragmentInteractionListener} interface
 * to handle interaction events.
 * Use the {@link DataAcquisitionMode#newInstance} factory method to
 * create an instance of this fragment.
 */
public class DataAcquisitionMode extends Fragment {
    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";
    private String ServerIP;
    private String CLS;
    private Handler mainHandler;
    private TextView speed;
    private Switch saveToFile;
    private updateGUI updateGUIRunnable = new updateGUI();
    private GPSManager gps;
    DataAcquisition configurator;
    public DateFormat df = new DateFormat();
    private File fobj = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath(), "testy");
    public File newfile;
    FileOutputStream stream;

    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;

    private OnFragmentInteractionListener mListener;

    public DataAcquisitionMode() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment DataAcquisitionMode.
     */
    // TODO: Rename and change types and number of parameters
    public static DataAcquisitionMode newInstance(String param1, String param2) {
        DataAcquisitionMode fragment = new DataAcquisitionMode();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Bundle bundle = this.getArguments();
        if (bundle != null) {
            ServerIP= bundle.getString(getString(R.string.SERVER_IP_KEY));
            CLS = bundle.getString(getString(R.string.CLS_KEY));
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view =  inflater.inflate(R.layout.fragment_data_acquisition_mode, container, false);
        GridView gv = view.findViewById(R.id.gv);
        LazyAdapter adapter = new LazyAdapter(this.getContext(), getResources().getStringArray(R.array.TAGS));
        gv.setAdapter(adapter);
        this.requestPermissions();
        saveToFile = view.findViewById(R.id.saveToFile);
        speed = view.findViewById(R.id.speed);
        gps = new GPSManager(getContext(), "DATA ACQUISITION");
        configurator = new DataAcquisition(getContext(), mainHandler, "DATA ACQUISITION", null, gps);
        mainHandler = new Handler();
        saveToFile.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    if (!configurator.configure())
                        Toast.makeText(getContext(), "Unable to start thread(no r/w permission)", Toast.LENGTH_LONG);
                    gps.configure();
                    configure_event_file();
                    mainHandler.post(updateGUIRunnable);
                    Set<Thread> threadSet = Thread.getAllStackTraces().keySet();
                    Log.e("active threads", threadSet.toString());
                } else {
                    configurator.cleanThread();
                    gps.cleanThread();
                    closeFile();
                    mainHandler.removeCallbacks(updateGUIRunnable);
                    Set<Thread> threadSet = Thread.getAllStackTraces().keySet();
                    Log.e("active threads", threadSet.toString());
                }
            }
        });
        gv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View v,
                                    int position, long id) {
                if(saveToFile.isChecked()){

                    Toast.makeText(getContext(), "Wybrano:\n" + getResources().getStringArray(R.array.TAGS)[position],
                            Toast.LENGTH_SHORT).show();
                    Date currentTime = Calendar.getInstance().getTime();
                    String date = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss:SSS").format(currentTime);
                    String toWrite = date + ";" + getResources().getStringArray(R.array.TAGS)[position] + "\r\n";
                    try {
                        stream.write(toWrite.getBytes());
                    } catch (Exception ex) {
                        Log.e("TE3ST", ex.getMessage().toString());
                    }
                }
            }
        });
        return view;
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
    @Override
    public void onRequestPermissionsResult(int requestCode,
                                           String permissions[], int[] grantResults) {
        switch (requestCode) {
            case 1:
            case 2: {
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
        if (ContextCompat.checkSelfPermission(this.getActivity(),
                Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this.getActivity(),
                    new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},
                    getResources().getInteger(R.integer.READING_PERMISSIONS));
        } else {
            // Permission has already been granted
            Log.e("Permissions", "Reading permission has already been granted");
        }
        // the same for writing
        if (ContextCompat.checkSelfPermission(this.getActivity(),
                Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this.getActivity(),
                    new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                    getResources().getInteger(R.integer.READING_PERMISSIONS));
        } else {
            // Permission has already been granted
            Log.e("Permissions", "Writing permissions has already been granted");
        }
    }
    // TODO: Rename method, update argument and hook method into UI event
    public void onButtonPressed(Uri uri) {
        if (mListener != null) {
            mListener.onFragmentInteraction(uri);
        }
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnFragmentInteractionListener) {
            mListener = (OnFragmentInteractionListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnFragmentInteractionListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }
    @Override
    public void onStop(){
        if(saveToFile.isChecked()){
            configurator.cleanThread();
            gps.cleanThread();
            closeFile();
            mainHandler.removeCallbacks(updateGUIRunnable);
            Set<Thread> threadSet = Thread.getAllStackTraces().keySet();
            Log.e("active threads", threadSet.toString());
        }
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.DATA_ACTIVITY_FRAGMENT),"++ ON STOP ++");
        super.onStop();


    }
    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnFragmentInteractionListener {
        // TODO: Update argument type and name
        void onFragmentInteraction(Uri uri);
    }
    class updateGUI implements Runnable {
        @Override
        public void run() {
            try {
                speed.setText(String.valueOf(gps.speed*3.6));
            } catch (Exception e) {
                // TODO: handle exception
            } finally {
                //also call the same runnable to call it at regular interval
                mainHandler.postDelayed(this, 30);
            }
        }
    }
    public void onStart() {
        super.onStart();
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.DATA_ACTIVITY_FRAGMENT),"++ ON START ++");
        //configurator.onStart();
    }

    @Override
    public void onResume() {
        super.onResume();
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.DATA_ACTIVITY_FRAGMENT),"+ ON RESUME +");
    }

    @Override
    public void onPause() {
        super.onPause();
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.DATA_ACTIVITY_FRAGMENT),"- ON PAUSE -");
    }
}
