using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ProjectileThrower : MonoBehaviour
{
    [SerializeField] private Transform cannon;
    [SerializeField] private Transform muzzle;

    [SerializeField] private Slider initialVelSlider;
    [SerializeField] private Slider launchAngleSlider;
    [SerializeField] private Slider gravitySlider;
    [SerializeField] private Slider airdragSlider;
    [SerializeField] private Button launchButton;

    [SerializeField] private GameObject ballPrefab;

    [SerializeField] private float shootCooldown = 0.5f;
    private float cooldownTimer=0f;
    private float airResistanceValue;

    [SerializeField] private Text maxHeightText;
    [SerializeField] private Text timeOfFlightText;
    [SerializeField] private Text rangeText;

    [SerializeField] private Text actualMaxHeightText;
    [SerializeField] private Text actualFlightTimeText;
    [SerializeField] private Text actualRangeText;

    private float rotZ;
    void Start()
    {
        launchAngleSlider.onValueChanged.AddListener(v => { rotZ = v; UpdateCannonAngle(); });
        airdragSlider.onValueChanged.AddListener(v => { airResistanceValue = v; });

        launchButton.onClick.AddListener(LaunchBall);

    }

    // Update is called once per frame
    void Update()
    {
        cooldownTimer -= Time.deltaTime;
    }

    void UpdateCannonAngle()
    {
        cannon.localRotation = Quaternion.Euler(0f, 0f, rotZ);
    }

    void LaunchBall()
    {
        if(cooldownTimer <= 0f)
        {
            GameObject ball = Instantiate(ballPrefab, muzzle.position, Quaternion.identity);
            Destroy(ball, 5f);
            Rigidbody2D rb = ball.GetComponent<Rigidbody2D>();

            if (rb == null)
            {
                Debug.LogWarning("Ball prefab needs a Rigidbody2D!");
                return;
            }

            float angleRad = rotZ * Mathf.Deg2Rad;
            Vector2 direction = new Vector2(Mathf.Cos(angleRad), Mathf.Sin(angleRad)).normalized;
            float velocity = initialVelSlider.value;
            rb.velocity = direction * velocity;
            rb.drag = airResistanceValue;
            rb.gravityScale = gravitySlider.value / 9.81f;

            float uY = velocity * Mathf.Sin(angleRad);
            float uX = velocity * Mathf.Cos(angleRad);

            float maxHeight = (uY * uY) / (2f * gravitySlider.value);
            float timeOfFlight = (2f * uY) / gravitySlider.value;
            float range = velocity * velocity * Mathf.Sin(2f * angleRad) / gravitySlider.value;

            // === Update UI Texts ===
            maxHeightText.text = $"{maxHeight:F2} m";
            timeOfFlightText.text = $"{timeOfFlight:F2} s";
            rangeText.text = $"{range:F2} m";

            ProjectileStats stats = ball.GetComponent<ProjectileStats>();
            if (stats)
            {
                stats.Setup(actualMaxHeightText, actualFlightTimeText, actualRangeText);
            }

            cooldownTimer =shootCooldown;
        }

        
    }
}
