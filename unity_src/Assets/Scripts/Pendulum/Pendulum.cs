using UnityEngine;
using UnityEngine.UI;

public class Pendulum : MonoBehaviour
{
    [Header("References")]
    public Transform mount;
    public Transform arm;
    public Transform bob;

    [Header("UI")]
    public Slider lengthSlider;
    public Slider massSlider;
    public Slider gravitySlider;
    public Image keBar, peBar, teBar;
    public Text periodText;

    // state variables
    private float L, m, g;
    private float angle = 45f * Mathf.Deg2Rad;
    private float ω = 0f; // angular velocity

    private Vector3 prevVelocity;
    private Vector3 prevPos;

    [SerializeField] private GameObject arrowPrefab;
    private GameObject velocityArrow;
    private GameObject accelerationArrow;

    private int length = 5;
    void Start()
    {

        lengthSlider.onValueChanged.AddListener(v => { L = v; CalculatePeriod(); });

        massSlider.onValueChanged.AddListener(v => {
            m = v;
        });

        gravitySlider.onValueChanged.AddListener(v => {

            g = v;
            CalculatePeriod();
        });

        L = lengthSlider.value;
        m = massSlider.value;
        g = gravitySlider.value;

        CalculatePeriod();
        ResetPendulum();

        //velocityArrow = Instantiate(arrowPrefab, bob.position, Quaternion.identity);
        //accelerationArrow= Instantiate(accelerationArrow, bob.position,Quaternion.identity);

        prevVelocity = Vector3.zero;
        prevPos = bob.position;
    }

    void Update()
    {
        SimulatePendulum();
        UpdateArmAndBob();
        UpdateEnergyBars();

        Vector3 velocity = (bob.position - prevPos) / Time.deltaTime;
        Vector3 acceleration = (velocity - prevVelocity) / Time.deltaTime;

        prevPos = bob.position;
        prevVelocity = velocity;
    }

    Vector3 GetPerpendicularAcceleration(Vector3 velocity, Vector3 acceleration)
    {
        if (velocity == Vector3.zero) return Vector3.zero;

        return acceleration - Vector3.Project(acceleration, velocity.normalized);
    }

    void UpdateArrow(GameObject arrow, Vector3 position, Vector3 direction, Color color)
    {
        if (direction.magnitude < 0.01f)
        {
            arrow.SetActive(false);
            return;
        }

        arrow.SetActive(true);
        arrow.transform.position = position;
        arrow.transform.up = direction.normalized;

        // Scale arrow based on magnitude (adjust scale factor as needed)
        float scaleFactor = Mathf.Clamp(direction.magnitude * 0.3f, 0.5f, 3f);
        arrow.transform.localScale = new Vector3(1, scaleFactor, 1);

    }

    void SimulatePendulum()
    {
        // θ'' = -(g/L) sin θ
        float α = -(g / L) * Mathf.Sin(angle);
        ω += α * Time.deltaTime;
        angle += ω * Time.deltaTime;
    }

    void UpdateArmAndBob()
    {
        Vector3 offset = new Vector3(Mathf.Sin(angle), -Mathf.Cos(angle), 0f) * (L*length);
        Vector3 bobPos = mount.position + offset;

        bob.position = bobPos;

        arm.position = mount.position + offset * 0.5f;
        arm.up = offset.normalized;

        arm.localScale = new Vector3(
            arm.localScale.x,
            L * length ,
            arm.localScale.z
        );
    }

    void UpdateEnergyBars()
    {
        // height above lowest point: h = L(1 − cos θ)
        float h = L * (1 - Mathf.Cos(angle));
        float pe = m * g * h;
        float ke = 0.5f * m * Mathf.Pow(ω * L, 2);  // v = ωL
        float te = ke + pe;

        // Normalize bars to a chosen max (for example, 2·m·g·L)
        float maxEnergy = m * g * 2f * L;
        peBar.fillAmount = Mathf.Clamp01(pe / maxEnergy);
        keBar.fillAmount = Mathf.Clamp01(ke / maxEnergy);
        teBar.fillAmount = Mathf.Clamp01(te / maxEnergy);
    }

    void CalculatePeriod()
    {
        float T = 2f * Mathf.PI * Mathf.Sqrt(L / Mathf.Max(g, 0.01f));
        periodText.text = $"Time Period (T) = {T:F2} s";
    }

    public void ResetPendulum()
    {
        // reset angle & velocity, then update positions
        angle = 45f * Mathf.Deg2Rad;
        ω = 0f;
        UpdateArmAndBob();
    }
}
