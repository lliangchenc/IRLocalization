package com.example.irlocalization;

import androidx.appcompat.app.AppCompatActivity;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.text.DecimalFormat;
import java.util.Calendar;

public class MainActivity extends AppCompatActivity {
    private String TAG = "MainActivity";
    private int port;
    private String host;

    EditText portEditText;
    EditText hostEditText;
    TextView IMUtextView;
    Button connectButton;
    Button startButton;

//    private IrEmitter mIrEmitter;
    private SensorManager mSensorManager;
    private RotationListener mListener;

    boolean startFlag = false;
    boolean connectFlag = false;

    Socket socket;
    PrintWriter out;
    BufferedReader in;

    long timestamp;

    private float[] mRotationMatrix = new float[9];
    private final float[] accelerometerReading = new float[3];
    private final float[] magnetometerReading = new float[3];
    Handler mRotMatHandler;
    Runnable mUpdateRotMat;
    final long UPDATE_ROT_MAT_TIME = 10;   // 10 ms

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

//        mIrEmitter = new IrEmitter(this);
        mSensorManager = (SensorManager)getSystemService(SENSOR_SERVICE);
        mListener = new RotationListener();

        portEditText = findViewById(R.id.editTextPort);
        hostEditText = findViewById(R.id.editTextHost);
        connectButton = findViewById(R.id.buttonConnect);
        startButton = findViewById(R.id.buttonStart);
        IMUtextView = findViewById(R.id.IMUtextView);

        startButton.setEnabled(false);
        connectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (!connectFlag) {
                    setUpSocket();
                    connectButton.setText("Disconnect");
                    connectFlag = true;
                    startButton.setEnabled(true);
                } else {
                    try {
                        socket.close();
                        connectButton.setText("Connect");
                        connectFlag = false;
                        startButton.setEnabled(false);
                    } catch (IOException e) {
                        Log.d(TAG, e.toString());
                        Toast.makeText(getBaseContext(), "Fail to close the socket", Toast.LENGTH_SHORT).show();
                    }
                }
            }
        });

        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
//                mIrEmitter.toggle();
                startFlag = !startFlag;
                if (startFlag) {
                    startButton.setText("End");
                    mRotMatHandler.postDelayed(mUpdateRotMat, UPDATE_ROT_MAT_TIME);
                } else {
                    startButton.setText("Start");
                    mRotMatHandler.removeCallbacks(mUpdateRotMat);
                }
            }
        });

        mRotMatHandler = new Handler();
        mUpdateRotMat = new Runnable() {
            @Override
            public void run() {
                SensorManager.getRotationMatrix(mRotationMatrix, null,
                        accelerometerReading, magnetometerReading);
                DecimalFormat format = new DecimalFormat(("0.000"));
                IMUtextView.setText(format.format(mRotationMatrix[3]) + " " + format.format(mRotationMatrix[4]) + " " + format.format(mRotationMatrix[5]));
                if (startFlag && out != null) {
                    out.println(mRotationMatrix[3] + " " + mRotationMatrix[4] + " " + mRotationMatrix[5]);
                }
                mRotMatHandler.postDelayed(this, UPDATE_ROT_MAT_TIME);
            }
        };
        mRotMatHandler.postDelayed(mUpdateRotMat, UPDATE_ROT_MAT_TIME);
    }

    @Override
    protected void onPause() {
        super.onPause();
        // make sure to turn our sensor off when the activity is paused
        mSensorManager.unregisterListener(mListener);
        mRotMatHandler.removeCallbacks(mUpdateRotMat);
    }

    @Override
    protected void onResume() {
        super.onResume();
        // enable our sensor when the activity is resumed
        Sensor accelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        if (accelerometer != null) {
            mSensorManager.registerListener(mListener, accelerometer,
                    SensorManager.SENSOR_DELAY_NORMAL, SensorManager.SENSOR_DELAY_UI);
        }
        Sensor magneticField = mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        if (magneticField != null) {
            mSensorManager.registerListener(mListener, magneticField,
                    SensorManager.SENSOR_DELAY_NORMAL, SensorManager.SENSOR_DELAY_UI);
        }
        if (startFlag) {
            mRotMatHandler.postDelayed(mUpdateRotMat, UPDATE_ROT_MAT_TIME);
        }
    }

    private void setUpSocket() {
        host = hostEditText.getText().toString();
        port = Integer.parseInt(portEditText.getText().toString());
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Log.d(TAG, host);
                    Log.d(TAG,String.valueOf(port));
                    socket = new Socket(host, port);
                    out = new PrintWriter(socket.getOutputStream(), true);
                    in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    while (true) {
                        Log.d(TAG, "??");
                        String res = in.readLine();
                        if (res != null) {
                            Log.d(TAG, "Send timestamp: " + timestamp);
                            Log.d(TAG, "Recv timestamp: " + System.currentTimeMillis());
                        }
                    }
                } catch (IOException e) {
                    Log.d(TAG, e.toString());
//                    Toast.makeText(getBaseContext(), "Fail to connect to server!", Toast.LENGTH_SHORT).show();
                }
            }
        }).start();
    }

    private class RotationListener implements SensorEventListener {
        public void onSensorChanged(SensorEvent event) {
            if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
                System.arraycopy(event.values, 0, accelerometerReading,
                        0, accelerometerReading.length);
            } else if (event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD) {
                System.arraycopy(event.values, 0, magnetometerReading,
                        0, magnetometerReading.length);
            }
        }
        public void onAccuracyChanged(Sensor sensor, int accuracy) {
        }
    }
}