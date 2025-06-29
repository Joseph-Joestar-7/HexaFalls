using UnityEngine;
using UnityEngine.SceneManagement;

public class SimMenu : MonoBehaviour
{
    public void LoadPendulum()
    {
        SceneManager.LoadScene("Pendulum");
    }
    public void LoadProjectileSim()
    {
        SceneManager.LoadScene("Projectile");
    }

    public void LoadRodTorqueSim()
    {
        SceneManager.LoadScene("Sim_RodTorque");
    }

    public void LoadFlameTestSim()
    {
        SceneManager.LoadScene("Sim_FlameTests");
    }

    public void QuitApp()
    {
        Application.Quit();
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false; // for editor
#endif
    }
}
