using UnityEngine;
using UnityEngine.UI;
using TMPro; // Required for TextMeshPro

public class SliderValueUI : MonoBehaviour
{
    [SerializeField] private Slider slider;
    [SerializeField] private TMP_Text valueText; 
    void Start()
    {
        UpdateValueDisplay(slider.value);

        slider.onValueChanged.AddListener(UpdateValueDisplay);
    }

    void UpdateValueDisplay(float value)
    {
        
        valueText.text = value.ToString("0.0"); 
    }

    void OnDestroy()
    {
        slider.onValueChanged.RemoveListener(UpdateValueDisplay);
    }
}