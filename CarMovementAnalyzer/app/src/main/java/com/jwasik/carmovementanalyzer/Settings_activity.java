package com.jwasik.carmovementanalyzer;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.Toast;

public class Settings_activity extends AppCompatActivity
        implements AdapterView.OnItemSelectedListener{
    private String SERVER_IP = "0.0.0.0";
    private String CLS= "SVM";
    private Boolean USE_GPS = true;
    private EditText et;
    private Button set_ip;
    private Switch use_gps;
    public void onItemSelected(AdapterView<?> parent, View view,
                               int pos, long id) {
        CLS = parent.getItemAtPosition(pos).toString();
        Toast.makeText(parent.getContext(),
                "Wybrano klasyfikator: " + CLS,
                Toast.LENGTH_SHORT).show();
        // An item was selected. You can retrieve the selected item using
        // parent.getItemAtPosition(pos)
    }

    public void onNothingSelected(AdapterView<?> parent) {
        // Another interface callback
    }
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings_activity);
        if(savedInstanceState!=null){
            SERVER_IP = savedInstanceState.get(getString(R.string.SERVER_IP_KEY)).toString();
            USE_GPS = (Boolean)savedInstanceState.getBoolean(getString(R.string.USE_GPS_KEY));
            CLS = savedInstanceState.get(getString(R.string.SERVER_IP_KEY)).toString();

        }
        else{
            SERVER_IP = getIntent().getStringExtra(getString(R.string.SERVER_IP_KEY));
            CLS = getIntent().getStringExtra(getString(R.string.CLS_KEY));
            USE_GPS = (Boolean)getIntent().getBooleanExtra(getString(R.string.USE_GPS_KEY), true);
            Log.e("adwdab", USE_GPS.toString());
        }
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setDisplayShowHomeEnabled(true);
        Spinner spinner;
        // Inflate the layout for this fragment
        spinner=  findViewById(R.id.spinner);
        // Create an ArrayAdapter using the string array and a default spinner layout
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.choices, android.R.layout.simple_spinner_item);
        // Specify the layout to use when the list of choices appears
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        // Apply the adapter to the spinner
        spinner.setAdapter(adapter);
        spinner.setOnItemSelectedListener(this);
        use_gps = findViewById(R.id.gpsSwitch);
        use_gps.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                USE_GPS=b;
            }
        });
        if(USE_GPS)
            use_gps.setChecked(true);
        et = findViewById(R.id.ServerIp);
        et.setText(SERVER_IP);
        set_ip  = findViewById(R.id.Set_Ip_Bttn);
        set_ip.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view){
                SERVER_IP = et.getText().toString();
                Toast.makeText(view.getContext(),
                        "Adres servera: " + SERVER_IP,
                        Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }
    @Override
    public void onRestoreInstanceState(Bundle savedInstanceState) {
        if(savedInstanceState!=null){
            SERVER_IP = savedInstanceState.get(getString(R.string.SERVER_IP_KEY)).toString();
            CLS = savedInstanceState.get(getString(R.string.CLS_KEY)).toString();
            USE_GPS = (Boolean)savedInstanceState.get(getString(R.string.USE_GPS_KEY));
        }
        //toRead.setText(savedInstanceState.getString(GAME_STATE_KEY));
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.SETTINGS_ACTIVITY), "++ onRestoreInstanceState ++");
    }

    @Override
    public void onSaveInstanceState(Bundle outState) {
        outState.putString(getString(R.string.SERVER_IP_KEY), SERVER_IP);
        outState.putString(getString(R.string.CLS_KEY), CLS);
        outState.putBoolean(getString(R.string.USE_GPS_KEY), USE_GPS);
        // call superclass to save any view hierarchy
        super.onSaveInstanceState(outState);
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.SETTINGS_ACTIVITY), "++ onSaveInstanceState ++");
    }
    public void onBackPressed() {
        //
        SERVER_IP = et.getText().toString();
        Bundle bundle = new Bundle();
        bundle.putString(getString(R.string.SERVER_IP_KEY), SERVER_IP);
        bundle.putString(getString(R.string.CLS_KEY), CLS);
        bundle.putBoolean(getString(R.string.USE_GPS_KEY), USE_GPS);
        Intent mIntent = new Intent();
        mIntent.putExtras(bundle);
        setResult(RESULT_OK, mIntent);
        super.onBackPressed();
    }
    @Override
    public void onStart() {
        super.onStart();
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.SETTINGS_ACTIVITY), "++ ON START ++");
        //configurator.onStart();
    }

    @Override
    public void onResume() {
        super.onResume();
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.SETTINGS_ACTIVITY), "+ ON RESUME +");
    }

    @Override
    public void onPause() {
        super.onPause();
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.SETTINGS_ACTIVITY), "- ON PAUSE -");
    }

    @Override
    public void onStop() {
        super.onStop();
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.SETTINGS_ACTIVITY), "-- ON STOP --");
        //configurator.onStop();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (getResources().getBoolean(R.bool.VERBOSE))
            Log.e(getString(R.string.SETTINGS_ACTIVITY), "- ON DESTROY -");
    }
}
