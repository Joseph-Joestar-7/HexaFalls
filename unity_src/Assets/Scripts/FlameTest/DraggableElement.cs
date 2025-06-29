using UnityEngine;
using UnityEngine.EventSystems;

public class DraggableElement : MonoBehaviour, IBeginDragHandler, IDragHandler, IEndDragHandler
{
    private Vector3 startPos;

    public string elementName; // Assign this in Inspector (e.g., "Sodium")

    public void OnBeginDrag(PointerEventData eventData)
    {
        startPos = transform.position;
    }

    public void OnDrag(PointerEventData eventData)
    {
        Vector3 pos = Camera.main.ScreenToWorldPoint(eventData.position);
        pos.z = 0f;
        transform.position = pos;
    }

    public void OnEndDrag(PointerEventData eventData)
    {
        // Optional: snap back if not dropped properly
    }
}
