package com.jwasik.acc_reader;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Log;

import java.util.ArrayList;
import java.util.LinkedList;

public class DataBaseManager extends SQLiteOpenHelper {

    public DataBaseManager(Context context) {
        super(context, "data_logs.db", null, 1);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("create table results(id integer primary key, " +
                "result text);");
    }

    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
    }

    public int getTableNumber() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT * FROM results ORDER BY ID DESC LIMIT 1", null);
        if (cursor.getCount() > 0) {
            cursor.moveToNext();
            return cursor.getInt(0);
        }
        return 0;
    }

    public void readTable() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT * FROM data_15", null);
        while(cursor.moveToNext()){
            int timestamp = cursor.getInt(0);
            float y = cursor.getFloat(1);
            float z = cursor.getFloat(2);
            Log.e("tag", String.valueOf(timestamp) + ", " + String.valueOf(y));
        }
    }

    public int insertIntoResultsTable(String result) {
        int tableNr = this.getTableNumber();
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("id", tableNr + 1);
        cv.put("result", result);
        db.insert("results", null, cv);
        return tableNr + 1;
    }

    public void fillDataTable(int tableNr, ArrayList<SensorData> data) {
        SQLiteDatabase db = getWritableDatabase();
        db.execSQL("create table data_" + String.valueOf(tableNr) + " (timestamp int, ax1 real, ax2 real, ax3 real);");
        Log.e("test", String.valueOf(tableNr));
        SensorData elem;
        for(int i =0; i<data.size();i++)
        {
            elem = data.get(i);
            ContentValues cv = new ContentValues();
            cv.put("timestamp", elem.getTimestamp());
            cv.put("ax1", elem.getData()[0]);
            cv.put("ax2", elem.getData()[1]);
            cv.put("ax3", elem.getData()[2]);
            db.insert("data_" + String.valueOf(tableNr), null, cv);
        }
    }
}

