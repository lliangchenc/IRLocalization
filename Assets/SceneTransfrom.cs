using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Microsoft.MixedReality.Toolkit.UI;

public class SceneTransfrom : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void OnDistanceChanged(SliderEventData eventData) {
    	ShowSliderValue ssv = GameObject.Find("Menu/DistanceSlider/ThumbRoot/ValueDistance").GetComponent<ShowSliderValue>();
    	float value = ssv.getValue(); 
    	Vector3 p = transform.position;
    	p.z = value;
    	transform.position = p;
    }

    public void OnLengthChanged(SliderEventData eventData) {
    	ShowSliderValue ssv = GameObject.Find("Menu/LengthSlider/ThumbRoot/ValueLength").GetComponent<ShowSliderValue>();
    	float value = ssv.getValue();


    	GameObject s = GameObject.Find("SphereLeft");
    	Vector3 p = s.transform.localPosition;
    	p.x = -value;
    	s.transform.localPosition = p;

    	s = GameObject.Find("SphereRight");
    	p = s.transform.localPosition;
    	p.x = value;
    	s.transform.localPosition = p;
    }
}
