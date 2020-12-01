/************************************************************************************

Copyright (c) Facebook Technologies, LLC and its affiliates. All rights reserved.  

See SampleFramework license.txt for license terms.  Unless required by applicable law 
or agreed to in writing, the sample code is provided �AS IS� WITHOUT WARRANTIES OR 
CONDITIONS OF ANY KIND, either express or implied.  See the license for specific 
language governing permissions and limitations under the license.

************************************************************************************/
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

namespace OculusSampleFramework
{
    public class DistanceGrabberSample : MonoBehaviour
    {

        bool useSpherecast = false;
        bool allowGrabThroughWalls = false;
        private RectTransform rt0, rt1, rt2, rt3, rt4, rt5;
        private Vector3 rel_vec;
        private float rel_ang, dist, tgt_sig;

        private Transform src_trans, tgt_trans;

        private string address = "172.20.10.4";
        private int port = 3417;

        private TcpClient client;
        private NetworkStream stream;
        Thread t;

        public bool UseSpherecast
        {
            get { return useSpherecast; }
            set
            {
                useSpherecast = value;
                for (int i = 0; i < m_grabbers.Length; ++i)
                {
                    m_grabbers[i].UseSpherecast = useSpherecast;
                }
            }
        }

        public bool AllowGrabThroughWalls
        {
            get { return allowGrabThroughWalls; }
            set
            {
                allowGrabThroughWalls = value;
                for (int i = 0; i < m_grabbers.Length; ++i)
                {
                    m_grabbers[i].m_preventGrabThroughWalls = !allowGrabThroughWalls;
                }
            }
        }

        [SerializeField]
        DistanceGrabber[] m_grabbers = null;

        // Use this for initialization
        void Start()
        {
            DebugUIBuilder.instance.AddLabel("IR Localization Sample");
            rt0 = DebugUIBuilder.instance.AddLabel("IR Localization Sample");
            rt1 = DebugUIBuilder.instance.AddLabel("IR Localization Sample");
            rt2 = DebugUIBuilder.instance.AddLabel("IR Localization Sample");
            rt3 = DebugUIBuilder.instance.AddLabel("IR Localization Sample");
            rt4 = DebugUIBuilder.instance.AddLabel("IR Localization Sample");
            rt5 = DebugUIBuilder.instance.AddLabel("IR Localization Sample");
            DebugUIBuilder.instance.Show();

			// Forcing physics tick rate to match game frame rate, for improved physics in this sample.
			// See comment in OVRGrabber.Update for more information.
			float freq = OVRManager.display.displayFrequency;
			if(freq > 0.1f)
			{
				Debug.Log("Setting Time.fixedDeltaTime to: " + (1.0f / freq));
				Time.fixedDeltaTime = 1.0f / freq;
			}
            
            //if (!Permission.HasUserAuthorizedPermission("android.permission.INTERNET"))
            Permission.RequestUserPermission("android.permission.INTERNET");
            ConnectToServer();
            
        }

        void Update(){
            src_trans = GameObject.Find("OVRCameraRig/TrackingSpace/RightHandAnchor").transform;
            tgt_trans = GameObject.Find("Sphere").transform;
            rel_vec = tgt_trans.position - src_trans.position;
            rel_ang = Vector3.Angle(src_trans.forward, rel_vec);
            dist = Vector3.Distance(tgt_trans.position, src_trans.position);
            tgt_sig = EngergyGain(rel_ang) / Mathf.Pow(dist, 2);
            rt1.GetComponent<Text>().text = "Src Pos " + src_trans.position.ToString("0.000");
            rt2.GetComponent<Text>().text = "Src Rot " + src_trans.forward.ToString("0.000");
            rt3.GetComponent<Text>().text = "Tgt Sig " + (100*tgt_sig).ToString("0.000");
            rt4.GetComponent<Text>().text = "Rel Vec " + (-rel_vec).ToString("0.000");
            GameObject.Find("Sphere").GetComponent<Renderer>().material.color = new Color(255,255,255) * tgt_sig;
            TcpSendMessage("[" + src_trans.forward.ToString("0.000000") + "," + (100*tgt_sig).ToString("0.000000") + "," + rel_vec.ToString("0.000000") + "]@");
        }

        public void ToggleSphereCasting(Toggle t)
        {
            UseSpherecast = !UseSpherecast;
        }

        public void ToggleGrabThroughWalls(Toggle t)
        {
            AllowGrabThroughWalls = !AllowGrabThroughWalls;
        }

        // ground-truth gain function
        private float EngergyGain(float x, float sigma=0.2f){
            float x_deg = x / 180.0f * Mathf.PI;
            return Mathf.Exp(-Mathf.Pow(Mathf.Tan(x_deg), 2.0f) / sigma / sigma) / sigma;
        }

        void ConnectToServer() {
            client = new TcpClient();
            while(!client.Connected){
                client.Connect(address, port);
            }
            
            rt0.GetComponent<Text>().text = "client.Connected: " + client.Connected;
            stream = client.GetStream();
            t = new Thread(TcpReceiveMessage);
            t.Start();
        }
            
        void TcpSendMessage(string myWrite) {
            byte[] data = Encoding.UTF8.GetBytes(myWrite);
            stream.Write(data, 0, data.Length);
        }

        //客户端接收消息
        void TcpReceiveMessage() {
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
                    rt5.GetComponent<Text>().text = "Pred Vec " + ss[index];
                }
                
            }
        }

    }
}
