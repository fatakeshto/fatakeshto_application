package com.abm.fatakeshto;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import com.google.firebase.firestore.FirebaseFirestore;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class AppListFetcher {
    private Context context;

    public AppListFetcher(DeviceService service) {
        this.context = service;
    }

    public void syncInstalledApps() {
        PackageManager pm = context.getPackageManager();
        List<ApplicationInfo> apps = pm.getInstalledApplications(0);
        List<String> appNames = new ArrayList<>();
        for (ApplicationInfo app : apps) {
            appNames.add(app.packageName);
        }
        FirebaseFirestore.getInstance().collection("installed_apps").add(new HashMap<String, Object>() {{
            put("apps", appNames);
            put("network_usage", "placeholder"); // Requires PACKAGE_USAGE_STATS
        }});
    }
}