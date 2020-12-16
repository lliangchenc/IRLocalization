using System;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Android;

using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;
using System.Threading;
using System.IO;

using Microsoft.MixedReality.Toolkit.Input;
using Microsoft.MixedReality.Toolkit.Utilities;

public class Server : MonoBehaviour
{
	[SerializeField]
	private string address = "10.0.0.3";
	[SerializeField]
	private int port = 3417;
	private TcpClient client;
	private NetworkStream stream;
	Thread t;

	private bool sendDataFlag;
	private bool emptyFrameFlag;
	string msg;

	// GameObject Reference
	GameObject sphereLeft;
	GameObject sphereRight;
	GameObject[] irReceivers;

    // Start is called before the first frame update
    void Start()
    {
        sphereLeft = GameObject.Find("SphereLeft");
        sphereRight = GameObject.Find("SphereRight");
        irReceivers = GameObject.FindGameObjectsWithTag("IrReceiver");

        Permission.RequestUserPermission("android.permission.INTERNET");
        ConnectToServer();
    }

    void OnDisable()
    {
    	if (client != null) {
    		client.Close();
    	}
    }

    // Update is called once per frame
    void Update()
    {
    	OVRInput.Update();	// recommended in OVR documentation
    	updateFlagWithController();
        if (sendDataFlag) {
        	if (HandJointUtils.TryGetJointPose(TrackedHandJoint.IndexTip, Handedness.Right, out MixedRealityPose pose)) {
        		/* sent data format:
				* [src.direction, src.position, 
				* ir_recv1.brightness, ir_recv1.rel_direction, 
				* ir_recv2.brightness, ir_recv2.rel_direction, ...]
        		*/

        		msg = "[";
        		msg += pose.Forward.ToString("0.000000") + ", ";
        		msg += pose.Position.ToString("0.000000");

	        	// support multi IR receiver
	        	foreach (GameObject irReceiver in irReceivers) {
	        		Transform tgt_trans = irReceiver.transform;
	        		Vector3 rel_vec = tgt_trans.position - pose.Position;
	        		float rel_ang = Vector3.Angle(pose.Forward, rel_vec);
	        		float dist = Vector3.Distance(tgt_trans.position, pose.Position);
	        		float tgt_sig = EnergyGain(rel_ang) / Mathf.Pow(dist, 2);
	        		msg += ", " + tgt_sig.ToString("0.000000");
	        		msg += ", " + rel_vec.ToString("0.000000");
	        	}
	        	msg += "]@";
	        	TcpSendMessage(msg);
			}
        }
    }

    private void updateFlagWithController() {
    	if (OVRInput.Get(OVRInput.Button.One)) {
    		// if Button 'A' is triggered in this frame, start/stop sending data
    		if (!sendDataFlag) {
    			TcpSendMessage(getSceneConfig());
    			sendDataFlag = true;
    		}
    	} else {
    		sendDataFlag = false;
    	}

    	if (OVRInput.Get(OVRInput.Button.Two)) {
    		// if Button 'B' is triggered, send an empty frame indicating the left/right edge
    		if (!emptyFrameFlag) {
    			TcpSendMessage("[]@");
    			emptyFrameFlag = true;
    		}
    	} else {
    		emptyFrameFlag = false;
    	}
    }

    private string getSceneConfig() {
    	ShowSliderValue distanceSlider = GameObject.Find("Menu/DistanceSlider/ThumbRoot/ValueDistance").GetComponent<ShowSliderValue>();
    	ShowSliderValue lengthSlider = GameObject.Find("Menu/LengthSlider/ThumbRoot/ValueLength").GetComponent<ShowSliderValue>();
    	string distance = distanceSlider.getValue().ToString("0.000000");
    	string length = lengthSlider.getValue().ToString("0.000000");
    	return $"[{distance}, {length}]@";
    }

    private void ConnectToServer() {
        client = new TcpClient();
        while(!client.Connected){
            client.Connect(address, port);
        }
        
        // rt0.GetComponent<Text>().text = "client.Connected: " + client.Connected;
        stream = client.GetStream();
        t = new Thread(TcpReceiveMessage);
        t.Start();
    }

    private void TcpSendMessage(string myWrite) {
        byte[] data = Encoding.UTF8.GetBytes(myWrite);
        stream.Write(data, 0, data.Length);
    }

    private void TcpReceiveMessage() {
        while (true)
        {
            if (client.Connected == false)
            {
                break;
            }
            byte[] data = new byte[1024];
            int length = stream.Read(data, 0, data.Length);
            string message = Encoding.UTF8.GetString(data, 0, length);
            string[] ss = message.Split('@');
            if (ss.Length >= 2){
                int index = ss.Length - 2;
                // rt5.GetComponent<Text>().text = "Pred Vec " + ss[index];
            }
            
        }
    }

    // ground-truth gain function
    private float EnergyGain(float x, float sigma=0.2f){
        float x_deg = x / 180.0f * Mathf.PI;
        return Mathf.Exp(-Mathf.Pow(Mathf.Tan(x_deg), 2.0f) / sigma / sigma) / sigma;
    }
}
