package com.abm.fatakeshto;

import android.os.Handler;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import org.json.JSONObject;

public class WebSocketManager {
    private OkHttpClient client;
    private WebSocket webSocket;
    private DeviceService service;

    public WebSocketManager(DeviceService service) {
        this.service = service;
        client = new OkHttpClient();
        connect();
    }

    private void connect() {
        Request request = new Request.Builder().url("ws://project-android-zm6z.onrender.com/").build();
        webSocket = client.newWebSocket(request, new WebSocketListener() {
            @Override
            public void onMessage(WebSocket webSocket, String text) {
                try {
                    JSONObject json = new JSONObject(text);
                    if ("command".equals(json.getString("type"))) {
                        service.executeCommand(json.getString("command"), json.optJSONObject("params"));
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }

            @Override
            public void onClosed(WebSocket webSocket, int code, String reason) {
                reconnect();
            }

            @Override
            public void onFailure(WebSocket webSocket, Throwable t, okhttp3.Response response) {
                reconnect();
            }
        });
    }

    private void reconnect() {
        new Handler().postDelayed(this::connect, 5000); // Retry every 5 seconds
    }

    public void sendMessage(String message) {
        if (webSocket != null) {
            webSocket.send(message);
        }
    }
}