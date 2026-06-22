package com.example.backend_java.dto;

public class BuildRequest {
    private String youtube_url;
    private String format;
    private boolean fastMode;

    public String getYoutube_url() {
        return youtube_url;
    }

    public void setYoutube_url(String youtube_url) {
        this.youtube_url = youtube_url;
    }

    public String getFormat() {
        return format != null ? format : "pdf";
    }

    public void setFormat(String format) {
        this.format = format;
    }

    public boolean isFastMode() {
        return fastMode;
    }

    public void setFastMode(boolean fastMode) {
        this.fastMode = fastMode;
    }
}
