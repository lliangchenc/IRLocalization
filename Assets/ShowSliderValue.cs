using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Microsoft.MixedReality.Toolkit.UI;
using TMPro;

public class ShowSliderValue : MonoBehaviour
{
    [SerializeField]
    private TextMesh textMesh = null;
    [SerializeField]
    private float minValue = 0;
    [SerializeField]
    private float maxValue = 1;
    [SerializeField]
    private string unit = "";

    private float value = 0.5F;

    public void OnSliderUpdated(SliderEventData eventData)
    {
        if (textMesh == null)
        {
            textMesh = GetComponent<TextMesh>();
        }

        if (textMesh != null)
        {
        	value = (float) (minValue + (maxValue - minValue) * eventData.NewValue);
            textMesh.text = $"{value:F2} {unit}";
        }
    }

    public float getValue() {
    	return value;
    }
}
