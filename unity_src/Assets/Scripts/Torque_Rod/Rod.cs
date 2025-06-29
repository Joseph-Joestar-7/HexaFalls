using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Rod : MonoBehaviour
{
    [SerializeField] Transform rodTransform;
    [SerializeField] Transform pivotTransform;

    [SerializeField] private Slider lengthSlider;
    [SerializeField] private Slider pivotSlider;

    private float L=1f;
    // Start is called before the first frame update
    void Start()
    {
        lengthSlider.onValueChanged.AddListener(v => { L = v; UpdateRodLength(); });

        pivotSlider.onValueChanged.AddListener(v => {
            UpdatePivotPosition(v);
        });

        L = lengthSlider.value;
        UpdateRodLength();

        // Center the pivot at start
        pivotSlider.value = 0f;

    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void UpdateRodLength()
    {
        rodTransform.localScale = new Vector3(
            L,
            rodTransform.localScale.y,
            rodTransform.localScale.z
        );

        float half = L * 0.5f;
        pivotSlider.minValue = -half;
        pivotSlider.maxValue = +half;

        pivotSlider.value = Mathf.Clamp(pivotSlider.value, pivotSlider.minValue, pivotSlider.maxValue);

        UpdatePivotPosition(pivotSlider.value);

    }

    void UpdatePivotPosition(float value)
    {
        Vector3 pos = pivotTransform.localPosition;
        pos.x = value;
        pivotTransform.localPosition = pos;
    }
}
