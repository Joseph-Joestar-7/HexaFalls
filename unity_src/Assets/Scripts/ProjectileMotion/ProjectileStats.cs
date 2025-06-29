using UnityEngine;
using UnityEngine.UI;

public class ProjectileStats : MonoBehaviour
{
    private float flightTime = 0f;
    private float maxHeight = 0f;
    private float launchX;
    private float launchY;

    private bool hasLanded = false;

    [Header("UI Display")]
    private Text actualMaxHeightText;
    private Text actualFlightTimeText;
    private Text actualRangeText;

    void Start()
    {
        launchX = transform.position.x;
        launchY = transform.position.y;
        maxHeight = 0f;
    }

    void Update()
    {
        if (hasLanded) return;

        // Update flight time and max height during flight
        flightTime += Time.deltaTime;
        maxHeight = Mathf.Max(maxHeight, transform.position.y - launchY);
    }

    public void Setup(Text maxH, Text flightT, Text rangeT)
    {
        actualMaxHeightText = maxH;
        actualFlightTimeText = flightT;
        actualRangeText = rangeT;
    }

    void OnCollisionEnter2D(Collision2D collision)
    {
        if (hasLanded) return; // Only handle first impact
        hasLanded = true;

        float range = transform.position.x - launchX;

        // Update the UI
        if (actualMaxHeightText) actualMaxHeightText.text = $"{maxHeight:F2} m";
        if (actualFlightTimeText) actualFlightTimeText.text = $"{flightTime:F2} s";
        if (actualRangeText) actualRangeText.text = $"{range:F2} m";

        
    }
}
