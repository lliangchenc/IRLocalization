package com.example.irlocalization;

import android.content.Context;
import android.hardware.ConsumerIrManager;
import android.util.Log;
import android.widget.Toast;

public class IrEmitter {
    private final String TAG = "IrEmitter";
    ConsumerIrManager cIr;
    int frequency;
    int[] pattern = {1000000}; // turn on for one second
    boolean hasIrEmitter;
    boolean isOn = false;
    Context ctx;
    Thread thread;
    Runnable runnable = new Runnable() {
        @Override
        public void run() {
            while (isOn) {
                cIr.transmit(frequency, pattern);
            }
        }
    };
    public IrEmitter(Context context) {
        ctx = context;
        cIr = (ConsumerIrManager) context.getSystemService(Context.CONSUMER_IR_SERVICE);
        hasIrEmitter = cIr.hasIrEmitter();
        if (hasIrEmitter) {
            ConsumerIrManager.CarrierFrequencyRange[] range = cIr.getCarrierFrequencies();
            if (range == null) {
                Toast.makeText(ctx, "Fail to get IR frequency", Toast.LENGTH_SHORT).show();
            } else {
//                frequency = range[0].getMinFrequency();
                frequency = 38000;
            }
        }
    }

    public void toggle() {
        if (!isOn) {
            // turn on
            if (!hasIrEmitter) {
                Toast.makeText(ctx, "This phone does not have IR emitter.", Toast.LENGTH_SHORT).show();
            } else {
                thread = new Thread(runnable);
                isOn = true;
                thread.start();
            }
        } else {
            // turn off
            isOn = false;
        }
    }
}