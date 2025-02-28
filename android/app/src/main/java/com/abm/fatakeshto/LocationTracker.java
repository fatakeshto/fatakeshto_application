package com.abm.fatakeshto;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import androidx.core.content.ContextCompat;
import com.google.firebase.firestore.FieldValue;
import com.google.firebase.firestore.FirebaseFirestore;
import java.util.HashMap;
import java.util.Map;

public class LocationTracker implements LocationListener {
    private LocationManager locationManager;
    private DeviceService service;

    public LocationTracker(DeviceService service) {
        this.service = service;
        locationManager = (LocationManager) service.getSystemService(Context.LOCATION_SERVICE);
        if (ContextCompat.checkSelfPermission(service, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 60000, 10, this);
        }
    }

    @Override
    public void onLocationChanged(Location location) {
        Map<String, Object> data = new HashMap<>();
        data.put("latitude", location.getLatitude());
        data.put("longitude", location.getLongitude());
        data.put("timestamp", FieldValue.serverTimestamp());
        FirebaseFirestore.getInstance().collection("locations").add(data);
        try {
            JSONObject json = new JSONObject();
            json.put("type", "location");
            json.put("latitude", location.getLatitude());
            json.put("longitude", location.getLongitude());
            service.getWebSocketManager().sendMessage(json.toString());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override public void onStatusChanged(String provider, int status, Bundle extras) {}
    @Override public void onProviderEnabled(String provider) {}
    @Override public void onProviderDisabled(String provider) {}
}