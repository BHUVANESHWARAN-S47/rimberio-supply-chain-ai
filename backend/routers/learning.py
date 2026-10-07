from fastapi import APIRouter
from backend.models.schemas import LearningMetricsResponse
from backend.services.learning_feedback import learning_engine

router = APIRouter(prefix="/api/learning", tags=["Continuous Learning & Model Calibration"])

@router.get("/metrics", response_model=LearningMetricsResponse)
def get_learning_metrics():
    """Fetch model accuracy, lead-time MAE/RMSE, and Retain/Negotiate/Switch confusion matrix."""
    return learning_engine.get_metrics()

@router.post("/recalibrate", response_model=LearningMetricsResponse)
def trigger_recalibration():
    """Trigger online model recalibration with historical fulfillment observations."""
    return learning_engine.trigger_recalibration()
