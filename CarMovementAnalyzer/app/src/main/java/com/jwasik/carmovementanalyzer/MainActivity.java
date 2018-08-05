package com.jwasik.carmovementanalyzer;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.util.Log;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

public class MainActivity extends AppCompatActivity
        implements OnlineMode.OnFragmentInteractionListener,
         DataAcquisitionMode.OnFragmentInteractionListener,
         NavigationView.OnNavigationItemSelectedListener {
    private String SERVER_IP = "0.0.0.0";
    private String CLS = "SVM";
    private boolean RET_FROM_SETTINGS = false;
    private String ActiveFragment;
    private Boolean useGps;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);
        FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
        setTitle("Online mode");
        ft.replace(R.id.mainFrame, (Fragment)new OnlineMode());
        ft.commit();
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();
        Fragment fragment = null;
        if (id == R.id.nav_camera) {
            fragment = new OnlineMode();
            setTitle("Online mode");
            ActiveFragment = "online mode";
            // Handle the camera action
        } else if (id == R.id.nav_gallery) {
            fragment = new DataAcquisitionMode();
            setTitle("Data acquisition");
            ActiveFragment = "data acquisition";
        } else if (id == R.id.nav_manage) {
            Intent i = new Intent(this, Settings_activity.class);
            i.putExtra(getString(R.string.SERVER_IP_KEY), SERVER_IP);
            i.putExtra(getString(R.string.CLS_KEY), CLS);
            i.putExtra(getString(R.string.USE_GPS_KEY), useGps);
            startActivityForResult(i, 1);
        } else if (id == R.id.nav_share) {

        } else if (id == R.id.nav_send) {

        }
        if (fragment != null) {
            FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
            ft.replace(R.id.mainFrame, fragment);
            //ft.addToBackStack(null);
            ft.commit();
        }
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        Log.e("aab", String.valueOf(resultCode));
            if (resultCode == RESULT_OK) {
                SERVER_IP = (String) data.getExtras().getString(getString(R.string.SERVER_IP_KEY));
                CLS = (String) data.getExtras().getString(getString(R.string.CLS_KEY));
                useGps = (Boolean)data.getExtras().getBoolean(getString(R.string.USE_GPS_KEY));
                Log.e(SERVER_IP, useGps.toString());
                RET_FROM_SETTINGS = true;
            }
    }
    @Override
    public void onFragmentInteraction(Uri uri) {
        // NOTE:  Code to replace the toolbar title based current visible fragment
        //getSupportActionBar().setTitle(title);
    }
    @Override
    public void onStart() {
        if(RET_FROM_SETTINGS){
            Fragment fragment;
            if(ActiveFragment == "data acquisition"){
                fragment = new DataAcquisitionMode();
                setTitle("Data acquisition");
            }
            else{
                fragment = new OnlineMode();
                setTitle("Online mode");
            }
            Bundle bundle = new Bundle();
            bundle.putString(getString(R.string.SERVER_IP_KEY), SERVER_IP);
            bundle.putString(getString(R.string.CLS_KEY), CLS);
            bundle.putBoolean(getString(R.string.USE_GPS_KEY), useGps);
            fragment.setArguments(bundle);
            FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
            ft.replace(R.id.mainFrame, fragment);
            //ft.addToBackStack(null);
            ft.commit();
        }

        super.onStart();
        if (getResources().getBoolean(R.bool.VERBOSE)) Log.e(getString(R.string.MAIN_ACTIVITY),
                "++ ON START ++");
        //configurator.onStart();
    }

    @Override
    public void onResume() {
        super.onResume();
            if (getResources().getBoolean(R.bool.VERBOSE)) Log.e(getString(R.string.MAIN_ACTIVITY), "+ ON RESUME +");
    }

    @Override
    public void onPause() {
        super.onPause();
        if (getResources().getBoolean(R.bool.VERBOSE)) Log.e(getString(R.string.MAIN_ACTIVITY), "- ON PAUSE -");
    }

    @Override
    public void onStop() {
        super.onStop();
        if (getResources().getBoolean(R.bool.VERBOSE)) Log.e(getString(R.string.MAIN_ACTIVITY), "-- ON STOP --");
        //configurator.onStop();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (getResources().getBoolean(R.bool.VERBOSE)) Log.e(getString(R.string.MAIN_ACTIVITY), "- ON DESTROY -");
    }
}
