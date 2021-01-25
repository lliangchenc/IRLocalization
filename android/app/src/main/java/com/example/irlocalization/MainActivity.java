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

import com.example.irlocalization.representation.MatrixF4x4;
import com.example.irlocalization.representation.Quaternion;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.text.DecimalFormat;

public class MainActivity extends AppCompatActivity {
    private String TAG = "MainActivity";
    private int port;
    private String host;

    EditText portEditText;
    EditText hostEditText;
    TextView IMUMagneticTextView;
    TextView IMUGyroTextView;
    TextView IMUTextView;
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

    Handler mQuatHandler;
    Runnable mUpdateQuat;

    final int UPDATE_QUAT_TIME = 10;

    long timeDelay;

    private static final float NS2S = 1.0f / 1000000000.0f;
    private final Quaternion deltaQuaternion = new Quaternion();
    private long timestamp;
    private static final double EPSILON = 0.1f;
    private double gyroscopeRotationVelocity = 0;
    private Quaternion correctedQuaternion = new Quaternion();
    protected final Object synchronizationToken = new Object();
    protected final Quaternion currentOrientationQuaternion = new Quaternion();
    protected final MatrixF4x4 currentOrientationRotationMatrix = new MatrixF4x4();
    private boolean initializedFlag = false;
    private int initialCount = 0;

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
        IMUMagneticTextView = findViewById(R.id.IMUMageneticTextView);
        IMUGyroTextView = findViewById(R.id.IMUGyroTextView);
        IMUTextView = findViewById(R.id.IMUTextView);

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
                    mQuatHandler.postDelayed(mUpdateQuat, UPDATE_QUAT_TIME);
                } else {
                    startButton.setText("Start");
                    mQuatHandler.removeCallbacks(mUpdateQuat);
                }
            }
        });

        mQuatHandler = new Handler();
        mUpdateQuat = new Runnable() {
            @Override
            public void run() {
//                SensorManager.getRotationMatrix(mRotationMatrixMagnetic, null,
//                        accelerometerReading, magnetometerReading);

                DecimalFormat format = new DecimalFormat(("0.00000"));
                double[] vec = new double[3];
                quatToForwardVec(currentOrientationQuaternion, vec);
                IMUGyroTextView.setText("Rot Vec: " +
                        format.format(vec[0]) + " " +
                        format.format(vec[1]) + " " +
                        format.format(vec[2])
                );
                IMUTextView.setText("Quat: " +
                        format.format(Math.abs(currentOrientationQuaternion.x())) + " " +
                        format.format(Math.abs(currentOrientationQuaternion.y())) + " " +
                        format.format(Math.abs(currentOrientationQuaternion.z())) + " " +
                        format.format(Math.abs(currentOrientationQuaternion.w()))
                );
                if (startFlag && out != null) {
                    new Thread(new Runnable() {
                        @Override
                        public void run() {
                            out.println(currentOrientationQuaternion.x() + " " + currentOrientationQuaternion.y() + " " + currentOrientationQuaternion.z() + " " + currentOrientationQuaternion.w());
                            out.flush();
                            timeDelay = System.currentTimeMillis();
                        }
                    }).start();
                }
                mQuatHandler.postDelayed(this, UPDATE_QUAT_TIME);
            }
        };
        mQuatHandler.postDelayed(mUpdateQuat, UPDATE_QUAT_TIME);
    }

    protected void quatToForwardVec(Quaternion quat, double[] vec) {
        double x = quat.x();
        double y = quat.y();
        double z = quat.z();
        double w = quat.w();
        vec[0] = 2 * y * z - 2 * w * x;
        vec[1] = x * x - y * y + z * z - w * w;
        vec[2] = 2 * z * w + 2 * x * y;
        double norm = Math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]);
        vec[0] /= norm;
        vec[1] /= norm;
        vec[2] /= norm;
    }

    @Override
    protected void onPause() {
        super.onPause();
        // make sure to turn our sensor off when the activity is paused
        mSensorManager.unregisterListener(mListener);
        mQuatHandler.removeCallbacks(mUpdateQuat);
    }

    @Override
    protected void onResume() {
        super.onResume();
        // enable our sensor when the activity is resumed
        Sensor rotationVector = mSensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR);
        if (rotationVector != null) {
            mSensorManager.registerListener(mListener, rotationVector, SensorManager.SENSOR_DELAY_GAME);
        }
//        Sensor accelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
//        if (accelerometer != null) {
//            mSensorManager.registerListener(mListener, accelerometer,
//                    SensorManager.SENSOR_DELAY_NORMAL, SensorManager.SENSOR_DELAY_UI);
//        }
//        Sensor magneticField = mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
//        if (magneticField != null) {
//            mSensorManager.registerListener(mListener, magneticField,
//                    SensorManager.SENSOR_DELAY_NORMAL, SensorManager.SENSOR_DELAY_UI);
//        }
        Sensor gyroscope = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        if (gyroscope != null) {
            mSensorManager.registerListener(mListener, gyroscope, SensorManager.SENSOR_DELAY_GAME);
        }
        if (startFlag) {
            mQuatHandler.postDelayed(mUpdateQuat, UPDATE_QUAT_TIME);
        }
        initializedFlag = false;
        initialCount = 0;
    }

    private void setUpSocket() {
        host = hostEditText.getText().toString();
        port = Integer.parseInt(portEditText.getText().toString());
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    socket = new Socket(host, port);
                    Log.d(TAG, String.valueOf(socket.isConnected()));
                    Log.d(TAG, String.valueOf(socket.isClosed()));
                    out = new PrintWriter(socket.getOutputStream(), true);
                    in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    while (true) {
                        Log.d(TAG, "Reading");
                        in.readLine();
                        timeDelay = (System.currentTimeMillis() - timeDelay) / 2;
                        Log.d(TAG, "time delay is " + timeDelay);
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
            if (event.sensor.getType() == Sensor.TYPE_GYROSCOPE /* && initializedFlag */) {
                // This timestamps delta rotation to be multiplied by the current rotation
                // after computing it from the gyro sample data.
                if (timestamp != 0) {
                    final float dT = (event.timestamp - timestamp) * NS2S;
                    // Axis of the rotation sample, not normalized yet.
                    float axisX = event.values[0];
                    float axisY = event.values[1];
                    float axisZ = event.values[2];

                    // Calculate the angular speed of the sample
                    gyroscopeRotationVelocity = Math.sqrt(axisX * axisX + axisY * axisY + axisZ * axisZ);

                    // Normalize the rotation vector if it's big enough to get the axis
                    if (gyroscopeRotationVelocity > EPSILON) {
                        axisX /= gyroscopeRotationVelocity;
                        axisY /= gyroscopeRotationVelocity;
                        axisZ /= gyroscopeRotationVelocity;
                    }

                    // Integrate around this axis with the angular speed by the timestep
                    // in order to get a delta rotation from this sample over the timestep
                    // We will convert this axis-angle representation of the delta rotation
                    // into a quaternion before turning it into the rotation matrix.
                    double thetaOverTwo = gyroscopeRotationVelocity * dT / 2.0f;
                    double sinThetaOverTwo = Math.sin(thetaOverTwo);
                    double cosThetaOverTwo = Math.cos(thetaOverTwo);
                    deltaQuaternion.setX((float) (sinThetaOverTwo * axisX));
                    deltaQuaternion.setY((float) (sinThetaOverTwo * axisY));
                    deltaQuaternion.setZ((float) (sinThetaOverTwo * axisZ));
                    deltaQuaternion.setW(-(float) cosThetaOverTwo);

                    // Matrix rendering in CubeRenderer does not seem to have this problem.
                    synchronized (synchronizationToken) {
                        // Move current gyro orientation if gyroscope should be used
                        deltaQuaternion.multiplyByQuat(currentOrientationQuaternion, currentOrientationQuaternion);
                    }

                    correctedQuaternion.set(currentOrientationQuaternion);
                    // We inverted w in the deltaQuaternion, because currentOrientationQuaternion required it.
                    // Before converting it back to matrix representation, we need to revert this process
                    correctedQuaternion.w(-correctedQuaternion.w());

                    synchronized (synchronizationToken) {
                        // Set the rotation matrix as well to have both representations
                        SensorManager.getRotationMatrixFromVector(currentOrientationRotationMatrix.matrix,
                                correctedQuaternion.array());
                    }
                }
                timestamp = event.timestamp;
            }
//            else if (event.sensor.getType() == Sensor.TYPE_ROTATION_VECTOR && !initializedFlag) {
//                currentOrientationQuaternion.setX(event.values[0]);
//                currentOrientationQuaternion.setY(event.values[1]);
//                currentOrientationQuaternion.setZ(event.values[2]);
//                currentOrientationQuaternion.setW(event.values[3]);
//                correctedQuaternion.set(currentOrientationQuaternion);
//                correctedQuaternion.w(-correctedQuaternion.w());
//                synchronized (synchronizationToken) {
//                    SensorManager.getRotationMatrixFromVector(currentOrientationRotationMatrix.matrix,
//                            correctedQuaternion.array());
//                }
//                initialCount++;
//                if (initialCount > 100)
//                    initializedFlag = true;
//            }
        }
        public void onAccuracyChanged(Sensor sensor, int accuracy) {
        }
    }
}