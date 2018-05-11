package com.jwasik.acc_reader;

/**
 * Created by kuba on 2018-05-07.
 */

import java.util.ArrayList;
import java.util.HashMap;

import android.app.Activity;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

public class LazyAdapter extends BaseAdapter {
    private Context mContext;
    private String[] names;
    private static LayoutInflater inflater=null;
    public LazyAdapter(Context c, String[] names) {
        mContext = c;
        this.names = names;
        inflater = (LayoutInflater)mContext.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
    }

    public int getCount() {
        return names.length;
    }

    public Object getItem(int position) {
        return null;
    }

    public long getItemId(int position) {
        return 0;
    }

    // create a new ImageView for each item referenced by the Adapter
    public View getView(int position, View convertView, ViewGroup parent) {
        View vi=convertView;
        if(convertView==null)
            vi = inflater.inflate(R.layout.layout, null);
        TextView tv = (TextView)vi.findViewById(R.id.maneuver);
        tv.setText(this.names[position]);
        return vi;

    }
}