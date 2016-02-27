package net.ossrs.greenhouse;

import android.os.Handler;
import android.os.Message;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class MainActivity extends ActionBarActivity {
    private final String TAG = "GreenHouse";
    private Handler handler;
    private Thread worker;
    private HttpURLConnection conn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    @Override
    protected void onResume() {
        super.onResume();

        final int[] count = {0};
        handler = new Handler(new Handler.Callback() {
            @Override
            public boolean handleMessage(Message msg) {
                if (msg.what != 100) {
                    return false;
                }

                Bundle b = msg.getData();
                String summary = String.format("%d: 温室(%s,%d*C,%d%%), 外部(%d*C,%d%%)",
                        ++count[0], b.getString("s"), b.getInt("t"), b.getInt("h"),
                        b.getInt("ts"), b.getInt("hs"));
                Log.i(TAG, summary);

                TextView txt = (TextView)findViewById(R.id.txt_main);
                txt.setText(summary);
                return true;
            }
        });
        worker = new Thread(new Runnable() {
            @Override
            public void run() {
                while (!Thread.currentThread().isInterrupted()) {
                    for (int i = 0; i < 100; i++) {
                        try {
                            Thread.sleep(30);
                        } catch (InterruptedException e) {
                            Log.i(TAG, "Thread interrupted.");
                            return;
                        }
                    }

                    Bundle b = new Bundle();
                    b.putString("s", "unknown");
                    b.putInt("t", 0);
                    b.putInt("h", 0);
                    b.putInt("ts", 0);
                    b.putInt("hs", 0);

                    URL url = null;
                    try {
                        url = new URL("http://ossrs.net:8085/api/v1/servers");
                    } catch (MalformedURLException e) {
                        Log.i(TAG, "URL create failed.");
                        e.printStackTrace();
                        continue;
                    }

                    try {
                        Log.i(TAG, "Start to fetch data.");
                        conn = (HttpURLConnection) url.openConnection();
                        conn.setConnectTimeout(3000);
                        conn.setReadTimeout(30000);
                        conn.setRequestMethod("GET");
                        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));

                        JSONTokener parser = new JSONTokener(br.readLine());
                        JSONArray servers = (JSONArray)parser.nextValue();
                        for (int i = 0; i < servers.length(); i++) {
                            JSONObject server = (JSONObject)servers.get(i);
                            if (!"raspberrypi2".equals(server.getString("device_id"))) {
                                continue;
                            }

                            if (!server.has("devices")) {
                                continue;
                            }
                            JSONObject devices = (JSONObject)server.get("devices");

                            if (!devices.has("greenhouse") || !devices.has("space")) {
                                continue;
                            }
                            JSONObject greehouse = (JSONObject)devices.get("greenhouse");
                            JSONObject space = (JSONObject)devices.get("space");

                            b.putString("s", greehouse.getString("state"));
                            b.putInt("t", greehouse.getInt("temperature"));
                            b.putInt("h", greehouse.getInt("humidity"));
                            b.putInt("ts", space.getInt("temperature"));
                            b.putInt("hs", space.getInt("humidity"));
                            break;
                        }

                        Log.i(TAG, "Fetch data ok");
                    } catch (IOException e) {
                        Log.i(TAG, "Fetch IO failed.");
                        e.printStackTrace();
                        continue;
                    } catch (JSONException e) {
                        Log.i(TAG, "Fetch JSON failed.");
                        e.printStackTrace();
                        continue;
                    } finally {
                        if (conn != null) {
                            conn.disconnect();
                            conn = null;
                        }
                    }

                    Message msg = new Message();
                    msg.what = 100;
                    msg.setData(b);
                    handler.sendMessage(msg);
                }
                Log.i(TAG, "Worker thread ok.");
            }
        });
        worker.start();
    }

    @Override
    protected void onPause() {
        super.onPause();

        Log.i(TAG, "Paused to stop thread.");
        // interrupt the thread in sleep state.
        worker.interrupt();
        // interrupt the thread in io state.
        if (conn != null) {
            // it's important to close the connection,
            // or the thread maybe blocked in io(read/write),
            // for example, the server is slow or tcp retransmit.
            conn.disconnect();
        }

        // wait for thread to quit, it must quit.
        try {
            worker.join();
        } catch (InterruptedException e) {
            e.printStackTrace();

        }
        Log.i(TAG, "Thread terminated.");
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
}
