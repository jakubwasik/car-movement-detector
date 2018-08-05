package com.jwasik.carmovementanalyzer;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.ActivityCompat;
import android.support.v4.app.Fragment;
import android.support.v4.content.ContextCompat;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.Switch;
import android.widget.TextView;

import org.w3c.dom.Text;

import java.sql.Connection;
import java.util.Set;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link OnlineMode.OnFragmentInteractionListener} interface
 * to handle interaction events.
 * Use the {@link OnlineMode#newInstance} factory method to
 * create an instance of this fragment.
 */
public class OnlineMode extends Fragment {
    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";
    private GPSManager gps;
    public TCPClient client;
    DataAcquisition configurator;
    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;
    private Handler mainHandler;
    private String ServerIP;
    private String CLS;
    private Switch connectToServer;
    private OnFragmentInteractionListener mListener;
    private TextView event_detected;
    private TextView serverIpDisplay;
    private updateGUI updateGUIRunnable;
    private TextView connStatus;
    private TextView ClsStatus;
    private Boolean USE_GPS=true;
    private TextView gpsDisplay;
    public OnlineMode() {
        // Required empty public constructor
    }


    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment OnlineMode.
     */
    // TODO: Rename and change types and number of parameters
    public static OnlineMode newInstance(String param1, String param2) {
        OnlineMode fragment = new OnlineMode();
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
             USE_GPS = bundle.getBoolean(getString(R.string.USE_GPS_KEY));
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view= inflater.inflate(R.layout.fragment_online_mode, container, false);
        event_detected = view.findViewById(R.id.EventDetected
        );
        connectToServer = view.findViewById(R.id.connectToServer);
        serverIpDisplay = view.findViewById(R.id.ServerIp);
        connStatus = view.findViewById(R.id.ConnectionStatus);
        serverIpDisplay.setText(ServerIP);
        ClsStatus = view.findViewById(R.id.Cls);
        ClsStatus.setText(CLS);
        gpsDisplay = view.findViewById(R.id.GpsDisplay);
        if(USE_GPS)
            gpsDisplay.setText("włączony");
        else
            gpsDisplay.setText("wyłączony");

        this.requestPermissions();
        connectToServer.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                if(b){
                    client = new TCPClient(ServerIP, 8888, true, CLS);
                    client.connect();
                    gps = new GPSManager(getContext(), "ONLINE");
                    gps.configure();
                    configurator = new DataAcquisition(getContext(), mainHandler, "ONLINE", client, gps);
                    configurator.configure();
                }else{
                    configurator.cleanThread();
                    gps.cleanThread();
                    client.disconnect();
                    mainHandler.removeCallbacks(updateGUIRunnable);
                    Set<Thread> threadSet = Thread.getAllStackTraces().keySet();
                    Log.e("active threads", threadSet.toString());
                }
            }
        });
        // NOTE : We are calling the onFragmentInteraction() declared in the MainActivity
        // ie we are sending "Fragment 1" as title parameter when fragment1 is activated
        //if (mListener != null) {
         //   mListener.onFragmentInteraction("Fragment 1");
        //}

        // Here we will can create click listners etc for all the gui elements on the fragment.
        // For eg: Button btn1= (Button) view.findViewById(R.id.frag1_btn1);
        // btn1.setOnclickListener(...
        return view;
    }
    void requestPermissions(){
        // the same for INTERNET
        if (ContextCompat.checkSelfPermission(getContext(),
                Manifest.permission.INTERNET)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(getActivity(),
                    new String[]{Manifest.permission.INTERNET},
                    2);
        } else {
            Log.e("Permissions", "INTERNET permission has already been granted");
        }
    }
    class updateGUI implements Runnable {
        @Override
        public void run() {
            try {
                event_detected.setText(String.valueOf(client.event_detected));
                if(client.state== TCPClient.TcpClientState.CONNECTED)
                    connStatus.setText("connected");
                else
                    connStatus.setText("disconnected");
                if(USE_GPS)
                    gpsDisplay.setText("włączony");
                else
                    gpsDisplay.setText("wyłączony");
            } catch (Exception e) {
                // TODO: handle exception
            } finally {
                //also call the same runnable to call it at regular interval
                mainHandler.postDelayed(this, 30);
            }
        }
    }
    // TODO: Rename method, update argument and hook method into UI event
    public void onButtonPressed(Uri uri) {
        if (mListener != null) {
            mListener.onFragmentInteraction(uri);
        }
    }
    @Override
    public void onStop() {
        if(connectToServer.isChecked()){
            configurator.cleanThread();
            gps.cleanThread();
            client.disconnect();
            mainHandler.removeCallbacks(updateGUIRunnable);
            Set<Thread> threadSet = Thread.getAllStackTraces().keySet();
            Log.e("active threads", threadSet.toString());
        }

        super.onStop();
        if (getResources().getBoolean(R.bool.VERBOSE)) Log.e("qwe","-- ON STOP --");
        //configurator.onStop();
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
        updateGUIRunnable = new updateGUI();
        mainHandler = new Handler();
        mainHandler.post(updateGUIRunnable);
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
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
}